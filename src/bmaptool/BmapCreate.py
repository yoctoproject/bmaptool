# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# Copyright (c) 2012-2014 Intel, Inc.
# License: GPLv2
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This module implements the block map (bmap) creation functionality and provides
the corresponding API in form of the 'BmapCreate' class.

The idea is that while image files may generally be very large (e.g., 4GiB),
they may nevertheless contain only little real data, e.g., 512MiB. This data
are files, directories, file-system meta-data, partition table, etc. When
copying the image to the target device, you do not have to copy all the 4GiB of
data, you can copy only 512MiB of it, which is 4 times less, so copying should
presumably be 4 times faster.

The block map file is an XML file which contains a list of blocks which have to
be copied to the target device. The other blocks are not used and there is no
need to copy them. The XML file also contains some additional information like
block size, image size, count of mapped blocks, etc. There are also many
commentaries, so it is human-readable.

The image has to be a sparse file. Generally, this means that when you generate
this image file, you should start with a huge sparse file which contains a
single hole spanning the entire file. Then you should partition it, write all
the data (probably by means of loop-back mounting the image or parts of it),
etc. The end result should be a sparse file where mapped areas represent useful
parts of the image and holes represent useless parts of the image, which do not
have to be copied when copying the image to the target device.

This module uses the FIEMAP ioctl to detect holes.
"""

# Disable the following pylint recommendations:
#   *  Too many instance attributes - R0902
#   *  Too few public methods - R0903
# pylint: disable=R0902,R0903

import hashlib
import os
import threading
from concurrent.futures import ThreadPoolExecutor

from .BmapHelpers import human_size
from . import Filemap

# The bmap format version we generate.
#
# Changelog:
# o 1.3 -> 2.0:
#   Support SHA256 and SHA512 checksums, in 1.3 only SHA1 was supported.
#   "BmapFileChecksum" is used instead of "BmapFileSHA1", and "chksum="
#   attribute is used instead "sha1=". Introduced "ChecksumType" tag. This is
#   an incompatible change.
#   Note, bmap format 1.4 is identical to 2.0. Version 1.4 was a mistake,
#   instead of incrementing the major version number, we incremented minor
#   version number. Unfortunately, the mistake slipped into bmaptool version
#   3.0, and was only fixed in bmaptool v3.1.
SUPPORTED_BMAP_VERSION = "2.0"

# Mapped ranges at least this large are split into smaller ranges, so that
# their checksums can be calculated in parallel. This also makes the resulting
# bmap file more granular, which lets 'bmaptool verify' parallelize the
# verification. Ranges smaller than this are kept intact.
SPLIT_THRESHOLD = 64 * 1024 * 1024
# Size of the sub-ranges which large mapped ranges are split into.
SPLIT_SIZE = 32 * 1024 * 1024
# Amount of data read from the image file at once when calculating a checksum.
READ_CHUNK_SIZE = 8 * 1024 * 1024


def default_jobs():
    """Return the default number of checksum calculation threads."""
    return min(4, os.cpu_count() or 1)


def _normalize_jobs(jobs):
    """Validate and normalize the 'jobs' argument."""
    if jobs is None:
        return default_jobs()
    if jobs < 1:
        raise Error("number of jobs must be at least 1, got %d" % jobs)
    return jobs


_BMAP_START_TEMPLATE = """<?xml version="1.0" ?>
<!-- This file contains the block map for an image file, which is basically
     a list of useful (mapped) block numbers in the image file. In other words,
     it lists only those blocks which contain data (boot sector, partition
     table, file-system metadata, files, directories, extents, etc). These
     blocks have to be copied to the target device. The other blocks do not
     contain any useful data and do not have to be copied to the target
     device.

     The block map is an optimization which allows to copy or flash the image
     to the image quicker than copying of flashing the entire image. This is
     because with bmap less data is copied: <MappedBlocksCount> blocks instead
     of <BlocksCount> blocks.

     Besides the machine-readable data, this file contains useful commentaries
     which contain human-readable information like image size, percentage of
     mapped data, etc.

     The 'version' attribute is the block map file format version in the
     'major.minor' format. The version major number is increased whenever an
     incompatible block map format change is made. The minor number changes
     in case of minor backward-compatible changes. -->

<bmap version="%s">
    <!-- Image size in bytes: %s -->
    <ImageSize> %u </ImageSize>

    <!-- Size of a block in bytes -->
    <BlockSize> %u </BlockSize>

    <!-- Count of blocks in the image file -->
    <BlocksCount> %u </BlocksCount>

"""


class Error(Exception):
    """
    A class for exceptions generated by this module. We currently support only
    one type of exceptions, and we basically throw human-readable problem
    description in case of errors.
    """

    pass


class BmapCreate(object):
    """
    This class implements the bmap creation functionality. To generate a bmap
    for an image (which is supposedly a sparse file), you should first create
    an instance of 'BmapCreate' and provide:

    * full path or a file-like object of the image to create bmap for
    * full path or a file object to use for writing the results to

    Then you should invoke the 'generate()' method of this class. It will use
    the FIEMAP ioctl to generate the bmap.
    """

    def __init__(self, image, bmap, chksum_type="sha256", jobs=None):
        """
        Initialize a class instance:
        * image  - full path or a file-like object of the image to create bmap
                   for
        * bmap   - full path or a file object to use for writing the resulting
                   bmap to
        * chksum - type of the check sum to use in the bmap file (all checksum
                   types which python's "hashlib" module supports are allowed).
        * jobs   - number of threads to use for checksum calculation (defaults
                   to min(4, CPU count))
        """

        self.image_size = None
        self.image_size_human = None
        self.block_size = None
        self.blocks_cnt = None
        self.mapped_cnt = None
        self.mapped_size = None
        self.mapped_size_human = None
        self.mapped_percent = None

        self._mapped_count_pos1 = None
        self._mapped_count_pos2 = None
        self._chksum_pos = None

        self._f_image_needs_close = False
        self._f_bmap_needs_close = False

        self._jobs = _normalize_jobs(jobs)
        self._image_lock = threading.Lock()
        self._image_fd = None

        self._cs_type = chksum_type.lower()
        try:
            self._cs_len = len(hashlib.new(self._cs_type).hexdigest())
        except ValueError as err:
            raise Error(
                'cannot initialize hash function "%s": %s' % (self._cs_type, err)
            )

        if hasattr(image, "read"):
            self._f_image = image
            self._image_path = image.name
        else:
            self._image_path = image
            self._open_image_file()

        try:
            self._image_fd = self._f_image.fileno()
        except (AttributeError, OSError, ValueError):
            self._image_fd = None

        if hasattr(bmap, "read"):
            self._f_bmap = bmap
            self._bmap_path = bmap.name
        else:
            self._bmap_path = bmap
            self._open_bmap_file()

        try:
            self.filemap = Filemap.filemap(self._f_image)
        except (Filemap.Error, Filemap.ErrorNotSupp) as err:
            raise Error(
                "cannot generate bmap for file '%s': %s" % (self._image_path, err)
            )

        self.image_size = self.filemap.image_size
        self.image_size_human = human_size(self.image_size)
        if self.image_size == 0:
            raise Error(
                "cannot generate bmap for zero-sized image file '%s'" % self._image_path
            )

        self.block_size = self.filemap.block_size
        self.blocks_cnt = self.filemap.blocks_cnt

    def __del__(self):
        """The class destructor which closes the opened files."""
        if getattr(self, "_f_image_needs_close", False):
            self._f_image.close()
        if getattr(self, "_f_bmap_needs_close", False):
            self._f_bmap.close()

    def _open_image_file(self):
        """Open the image file."""
        try:
            self._f_image = open(self._image_path, "rb")
        except IOError as err:
            raise Error("cannot open image file '%s': %s" % (self._image_path, err))

        self._f_image_needs_close = True

    def _open_bmap_file(self):
        """Open the bmap file."""
        try:
            self._f_bmap = open(self._bmap_path, "w+")
        except IOError as err:
            raise Error("cannot open bmap file '%s': %s" % (self._bmap_path, err))

        self._f_bmap_needs_close = True

    def _bmap_file_start(self):
        """
        A helper function which generates the starting contents of the block
        map file: the header comment, image size, block size, etc.
        """

        # We do not know the amount of mapped blocks at the moment, so just put
        # whitespaces instead of real numbers. Assume the longest possible
        # numbers.

        xml = _BMAP_START_TEMPLATE % (
            SUPPORTED_BMAP_VERSION,
            self.image_size_human,
            self.image_size,
            self.block_size,
            self.blocks_cnt,
        )
        xml += "    <!-- Count of mapped blocks: "

        self._f_bmap.write(xml)
        self._mapped_count_pos1 = self._f_bmap.tell()

        xml = "%s or %s   -->\n" % (
            " " * len(self.image_size_human),
            " " * len("100.0%"),
        )
        xml += "    <MappedBlocksCount> "

        self._f_bmap.write(xml)
        self._mapped_count_pos2 = self._f_bmap.tell()

        xml = "%s </MappedBlocksCount>\n\n" % (" " * len(str(self.blocks_cnt)))

        # pylint: disable=C0301
        xml += "    <!-- Type of checksum used in this file -->\n"
        xml += "    <ChecksumType> %s </ChecksumType>\n\n" % self._cs_type

        xml += "    <!-- The checksum of this bmap file. When it is calculated, the value of\n"
        xml += '         the checksum has to be zero (all ASCII "0" symbols).  -->\n'
        xml += "    <BmapFileChecksum> "

        self._f_bmap.write(xml)
        self._chksum_pos = self._f_bmap.tell()

        xml = "0" * self._cs_len + " </BmapFileChecksum>\n\n"
        xml += (
            "    <!-- The block map which consists of elements which may either be a\n"
        )
        xml += "         range of blocks or a single block. The 'chksum' attribute\n"
        xml += "         (if present) is the checksum of this block range. -->\n"
        xml += "    <BlockMap>\n"
        # pylint: enable=C0301

        self._f_bmap.write(xml)

    def _bmap_file_end(self):
        """
        A helper function which generates the final parts of the block map
        file: the ending tags and the information about the amount of mapped
        blocks.
        """

        xml = "    </BlockMap>\n"
        xml += "</bmap>\n"

        self._f_bmap.write(xml)

        self._f_bmap.seek(self._mapped_count_pos1)
        self._f_bmap.write(
            "%s or %.1f%%" % (self.mapped_size_human, self.mapped_percent)
        )

        self._f_bmap.seek(self._mapped_count_pos2)
        self._f_bmap.write("%u" % self.mapped_cnt)

        self._f_bmap.seek(0)
        hash_obj = hashlib.new(self._cs_type)
        hash_obj.update(self._f_bmap.read().encode())
        chksum = hash_obj.hexdigest()
        self._f_bmap.seek(self._chksum_pos)
        self._f_bmap.write("%s" % chksum)

    def _read(self, size, offset):
        """
        Read up to 'size' bytes at 'offset' from the image file. 'pread()' is
        used when the image has a file descriptor, so that several threads can
        read the file concurrently without racing on the shared file position.
        """

        if self._image_fd is not None:
            return os.pread(self._image_fd, size, offset)

        with self._image_lock:
            self._f_image.seek(offset)
            return self._f_image.read(size)

    def _calculate_chksum_range(self, start, end):
        """
        A helper function which calculates checksum for the [start, end) byte
        range of the image file.
        """

        hash_obj = hashlib.new(self._cs_type)
        pos = start
        while pos < end:
            chunk = self._read(min(READ_CHUNK_SIZE, end - pos), pos)
            if not chunk:
                raise Error(
                    "unexpected end of image file '%s' at offset %d"
                    % (self._image_path, pos)
                )
            hash_obj.update(chunk)
            pos += len(chunk)

        return hash_obj.hexdigest()

    def _calculate_chksum(self, first, last):
        """
        A helper function which calculates checksum for the range of blocks of
        the image file: from block 'first' to block 'last'.
        """

        return self._calculate_chksum_range(
            first * self.block_size,
            min((last + 1) * self.block_size, self.image_size),
        )

    def _split_range(self, first, last):
        """
        Split a mapped block range into smaller ranges if it is at least
        'SPLIT_THRESHOLD' bytes long. Smaller ranges are returned intact.
        """

        size = (last - first + 1) * self.block_size
        if size < SPLIT_THRESHOLD:
            return [(first, last)]

        blocks = max(1, SPLIT_SIZE // self.block_size)
        result = []
        pos = first
        while pos <= last:
            end = min(pos + blocks - 1, last)
            result.append((pos, end))
            pos = end + 1

        return result

    def _iter_checksums(self, ranges, include_checksums):
        """
        Yield checksums for the block ranges in 'ranges', preserving the order
        of the ranges. Checksums are calculated in parallel when more than one
        job is configured.
        """

        if not include_checksums:
            for _ in ranges:
                yield None
            return

        if self._jobs == 1 or len(ranges) < 2:
            for first, last in ranges:
                yield self._calculate_chksum(first, last)
            return

        with ThreadPoolExecutor(max_workers=self._jobs) as executor:
            # Submit in bounded batches, so that a huge image does not create
            # millions of pending futures at once.
            batch_size = max(self._jobs * 4, 1)
            for index in range(0, len(ranges), batch_size):
                batch = ranges[index : index + batch_size]
                for chksum in executor.map(
                    lambda item: self._calculate_chksum(item[0], item[1]), batch
                ):
                    yield chksum

    def generate(self, include_checksums=True):
        """
        Generate bmap for the image file. If 'include_checksums' is 'True',
        also generate checksums for block ranges.
        """

        # Save image file position in order to restore it at the end
        image_pos = self._f_image.tell()

        self._bmap_file_start()

        # Split large mapped ranges, so that their checksums can be calculated
        # in parallel and the resulting bmap is more granular.
        ranges = []
        for first, last in self.filemap.get_mapped_ranges(0, self.blocks_cnt):
            ranges.extend(self._split_range(first, last))

        self.mapped_cnt = sum(last - first + 1 for first, last in ranges)

        # Generate the block map and write it to the XML block map file as we
        # go.
        for (first, last), chksum in zip(
            ranges, self._iter_checksums(ranges, include_checksums)
        ):
            if chksum is not None:
                chksum = ' chksum="%s"' % chksum
            else:
                chksum = ""

            if first != last:
                self._f_bmap.write(
                    "        <Range%s> %s-%s </Range>\n" % (chksum, first, last)
                )
            else:
                self._f_bmap.write("        <Range%s> %s </Range>\n" % (chksum, first))

        self.mapped_size = self.mapped_cnt * self.block_size
        self.mapped_size_human = human_size(self.mapped_size)
        self.mapped_percent = (self.mapped_cnt * 100.0) / self.blocks_cnt

        self._bmap_file_end()

        try:
            self._f_bmap.flush()
        except IOError as err:
            raise Error("cannot flush the bmap file '%s': %s" % (self._bmap_path, err))

        self._f_image.seek(image_pos)
