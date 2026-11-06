# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# Copyright (c) 2012-2014 Intel, Inc.
# License: GPLv2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This module implements the 'bmaptool verify' functionality and provides the
corresponding API in form of the 'BmapVerify' class.

The 'bmaptool verify' command is similar to 'sha256sum --check': it reads the
checksums stored in a bmap file and verifies the mapped block ranges of the
image file against them. The bmap file itself is verified too. Since the bmap
file does not contain the image path, the image path is derived by stripping
the '.bmap' suffix ('image.raw.bmap' -> 'image.raw'), unless it is passed
explicitly.
"""

import hashlib
import io
import logging
import os
import stat
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree

from .BmapHelpers import human_size

_log = logging.getLogger(__name__)  # pylint: disable=C0103

SUPPORTED_BMAP_VERSION = (2, 0)
READ_CHUNK_SIZE = 8 * 1024 * 1024
# Maximum amount of failed ranges reported, so that a completely broken image
# does not flood the terminal.
_MAX_REPORTED_FAILURES = 20

_METADATA_TAGS = frozenset(
    (
        "ImageSize",
        "BlockSize",
        "BlocksCount",
        "MappedBlocksCount",
        "ChecksumType",
        "BmapFileChecksum",
        "BmapFileSHA1",
    )
)


class Error(Exception):
    """A class for all the exceptions raised by this module."""

    pass


def default_jobs():
    """Return the default number of verification threads."""
    return min(4, os.cpu_count() or 1)


def _normalize_jobs(jobs):
    """Validate and normalize the 'jobs' argument."""
    if jobs is None:
        return default_jobs()
    if jobs < 1:
        raise Error("number of jobs must be at least 1, got %d" % jobs)
    return jobs


def derive_image_path(bmap_path):
    """
    Derive the image path from the bmap path by stripping the '.bmap' suffix.
    """

    if bmap_path.endswith(".bmap"):
        return bmap_path[: -len(".bmap")]

    raise Error(
        "cannot derive the image path from bmap file '%s': the file name does "
        "not end with '.bmap', please specify the image path explicitly"
        % bmap_path
    )


class BmapVerify(object):
    """
    This class implements verification of an image file against a bmap file.
    """

    def __init__(self, bmap_path, image_path=None, jobs=None, chksum_type=None):
        """
        Initialize a class instance:
        * bmap_path   - path to the bmap file (or a file-like object);
        * image_path  - path to the image file (or a file-like object); if not
                        specified, it is derived from 'bmap_path' by stripping
                        the '.bmap' suffix;
        * jobs        - number of verification threads (defaults to
                        min(4, CPU count));
        * chksum_type - if specified, the checksum type must match the one
                        stored in the bmap file.
        """

        self._f_bmap = None
        self._bmap_path = bmap_path
        if not hasattr(bmap_path, "read"):
            try:
                self._f_bmap = open(bmap_path, "rb")
            except OSError as err:
                raise Error("cannot open bmap file '%s': %s" % (bmap_path, err))

        self.image_path = image_path
        if self.image_path is None:
            if isinstance(bmap_path, (str, bytes, os.PathLike)):
                self.image_path = derive_image_path(os.fspath(bmap_path))
            else:
                raise Error(
                    "cannot derive the image path from a file-like bmap "
                    "object, please specify the image path explicitly"
                )
        self.jobs = _normalize_jobs(jobs)
        self._requested_cs_type = (
            chksum_type.lower() if chksum_type is not None else None
        )

        self.bmap_version = None
        self.block_size = None
        self.blocks_cnt = None
        self.image_size = None
        self.mapped_cnt = None
        self.cs_type = None
        self._cs_len = None
        self.ranges = []

        self.verified_ranges = 0
        self.skipped_ranges = 0
        self.verified_bytes = 0
        self.skipped_bytes = 0
        self.failures = []

    def __del__(self):
        """Close the bmap file if it was opened by this class."""
        if getattr(self, "_f_bmap", None) is not None:
            self._f_bmap.close()

    def _read_bmap(self):
        """Read the whole bmap file and return its contents as bytes."""
        try:
            if self._f_bmap is not None:
                self._f_bmap.seek(0)
                data = self._f_bmap.read()
            else:
                data = self._bmap_path.read()
        except OSError as err:
            raise Error("cannot read bmap file '%s': %s" % (self._bmap_path, err))

        if isinstance(data, str):
            data = data.encode()

        return data

    def _parse(self):
        """
        Parse the bmap file, validate its structure and the checksum of the
        bmap file itself.
        """

        data = self._read_bmap()
        version = None
        cs_attrib = "chksum"
        bmap_cs_tag = "BmapFileChecksum"
        ranges = []
        metadata = {}

        try:
            events = ElementTree.iterparse(
                io.BytesIO(data), events=("start", "end")
            )
            for event, elem in events:
                if event == "start":
                    if elem.tag == "bmap":
                        version = elem.attrib.get("version")
                        self.bmap_version = version
                        major, minor = self._parse_version(version)
                        if major == 1 and minor == 3:
                            cs_attrib = "sha1"
                            bmap_cs_tag = "BmapFileSHA1"
                    continue

                if elem.tag == "Range":
                    ranges.append(self._parse_range(elem, cs_attrib))
                    elem.clear()
                elif elem.tag in _METADATA_TAGS:
                    metadata[elem.tag] = (elem.text or "").strip()
                    elem.clear()
        except ElementTree.ParseError as err:
            raise Error(
                "cannot parse bmap file '%s': it is not a proper XML file: %s"
                % (getattr(self._bmap_path, "name", self._bmap_path), err)
            )

        if version is None:
            raise Error("bmap file '%s' has no version" % self._bmap_path)

        if bmap_cs_tag not in metadata:
            raise Error(
                "bmap file '%s' has no '%s' tag" % (self._bmap_path, bmap_cs_tag)
            )

        self._check_metadata(metadata, ranges, cs_attrib)
        self._verify_bmap_checksum(data, metadata[bmap_cs_tag], cs_attrib)
        self.ranges = ranges

    @staticmethod
    def _parse_version(version):
        """Parse the 'major.minor' bmap version string."""
        try:
            major, minor = (int(part) for part in version.split(".", 1))
        except (AttributeError, ValueError):
            raise Error("bad bmap version '%s'" % version)

        if major > SUPPORTED_BMAP_VERSION[0]:
            raise Error(
                "bmap version %s is not supported, only versions up to %d.%d "
                "are supported"
                % (version, SUPPORTED_BMAP_VERSION[0], SUPPORTED_BMAP_VERSION[1])
            )
        if major < 1 or (major == 1 and minor < 3):
            raise Error("bmap version %s does not contain checksums" % version)

        return major, minor

    @staticmethod
    def _parse_range(elem, cs_attrib):
        """Parse one '<Range>' XML element."""
        text = (elem.text or "").strip()
        split = [part.strip() for part in text.split("-", 1)]
        try:
            first = int(split[0])
            last = int(split[1]) if len(split) > 1 else first
        except ValueError:
            raise Error("bad block range '%s'" % text)

        if first < 0 or first > last:
            raise Error("bad block range '%s'" % text)

        return (first, last, elem.attrib.get(cs_attrib))

    def _check_metadata(self, metadata, ranges, cs_attrib):
        """Validate the bmap metadata and initialize geometry attributes."""

        required = ("ImageSize", "BlockSize", "BlocksCount")
        for tag in required:
            if tag not in metadata:
                raise Error("bmap file '%s' has no '%s' tag" % (self._bmap_path, tag))

        try:
            self.image_size = int(metadata["ImageSize"])
            self.block_size = int(metadata["BlockSize"])
            self.blocks_cnt = int(metadata["BlocksCount"])
        except ValueError as err:
            raise Error("bad bmap metadata in '%s': %s" % (self._bmap_path, err))

        if self.image_size <= 0 or self.block_size <= 0:
            raise Error("bad image geometry in bmap file '%s'" % self._bmap_path)

        expected_blocks = (self.image_size + self.block_size - 1) // self.block_size
        if expected_blocks != self.blocks_cnt:
            raise Error(
                "inconsistent bmap: image size %d does not match %d blocks of "
                "%d bytes"
                % (self.image_size, self.blocks_cnt, self.block_size)
            )

        self.mapped_cnt = None
        if "MappedBlocksCount" in metadata:
            try:
                self.mapped_cnt = int(metadata["MappedBlocksCount"])
            except ValueError as err:
                raise Error("bad 'MappedBlocksCount' value: %s" % err)

        if "ChecksumType" in metadata:
            self.cs_type = metadata["ChecksumType"].lower()
        elif cs_attrib == "sha1":
            self.cs_type = "sha1"
        else:
            raise Error("bmap file '%s' has no 'ChecksumType' tag" % self._bmap_path)

        try:
            self._cs_len = len(hashlib.new(self.cs_type).hexdigest())
        except ValueError as err:
            raise Error(
                'cannot initialize hash function "%s": %s' % (self.cs_type, err)
            )

        if (
            self._requested_cs_type is not None
            and self._requested_cs_type != self.cs_type
        ):
            raise Error(
                "checksum type mismatch: the bmap file uses '%s', but '%s' was "
                "requested" % (self.cs_type, self._requested_cs_type)
            )

        if not ranges:
            raise Error("bmap file '%s' contains no mapped ranges" % self._bmap_path)

        prev_last = -1
        for first, last, chksum in ranges:
            if first <= prev_last:
                raise Error(
                    "bad bmap: ranges are overlapping or not sorted "
                    "(range %d-%d follows block %d)" % (first, last, prev_last)
                )
            if last >= self.blocks_cnt:
                raise Error(
                    "bad bmap: range %d-%d is outside of the image "
                    "(%d blocks)" % (first, last, self.blocks_cnt)
                )
            if chksum is not None and len(chksum) != self._cs_len:
                raise Error(
                    "bad bmap: checksum '%s' has wrong length for '%s'"
                    % (chksum, self.cs_type)
                )
            prev_last = last

        total_blocks = sum(last - first + 1 for first, last, _ in ranges)
        if self.mapped_cnt is not None and total_blocks != self.mapped_cnt:
            raise Error(
                "inconsistent bmap: 'MappedBlocksCount' is %d, but the ranges "
                "contain %d blocks" % (self.mapped_cnt, total_blocks)
            )

        if all(chksum is None for _, _, chksum in ranges):
            raise Error(
                "bmap file '%s' contains no checksums, cannot verify the image "
                "(regenerate it with checksums enabled)" % self._bmap_path
            )

    def _verify_bmap_checksum(self, data, correct_chksum, cs_attrib):
        """Verify the checksum of the bmap file itself."""

        if cs_attrib == "sha1":
            tag = b"<BmapFileSHA1>"
        else:
            tag = b"<BmapFileChecksum>"

        tag_pos = data.find(tag)
        if tag_pos < 0:
            raise Error(
                "bmap file '%s' has no '%s' tag"
                % (self._bmap_path, tag.decode().strip("<>"))
            )

        start = tag_pos + len(tag)
        while start < len(data) and data[start : start + 1].isspace():
            start += 1

        correct = correct_chksum.encode()
        if data[start : start + len(correct)] != correct:
            raise Error(
                "cannot locate the checksum value in bmap file '%s'"
                % self._bmap_path
            )

        zeroed = data[:start] + b"0" * len(correct) + data[start + len(correct) :]
        calculated = hashlib.new(self.cs_type, zeroed).hexdigest()

        if calculated != correct_chksum:
            raise Error(
                "checksum mismatch for bmap file '%s': calculated '%s', "
                "should be '%s'" % (self._bmap_path, calculated, correct_chksum)
            )

    def _open_image(self):
        """Open the image file and validate its size."""
        try:
            fd = os.open(self.image_path, os.O_RDONLY)
        except OSError as err:
            raise Error("cannot open image file '%s': %s" % (self.image_path, err))

        try:
            st = os.fstat(fd)
        except OSError as err:
            os.close(fd)
            raise Error("cannot stat image file '%s': %s" % (self.image_path, err))

        if stat.S_ISREG(st.st_mode):
            if st.st_size < self.image_size:
                os.close(fd)
                raise Error(
                    "image file '%s' is too small: %d bytes, but the bmap "
                    "expects %d bytes (%s)"
                    % (
                        self.image_path,
                        st.st_size,
                        self.image_size,
                        human_size(self.image_size),
                    )
                )
            if st.st_size > self.image_size:
                _log.warning(
                    "image file '%s' is larger than the bmap image size "
                    "(%d > %d bytes), verifying the mapped ranges only",
                    self.image_path,
                    st.st_size,
                    self.image_size,
                )

        return fd

    def _hash_range(self, fd, first, last):
        """Calculate the checksum of the blocks in the [first, last] range."""
        start = first * self.block_size
        end = min((last + 1) * self.block_size, self.image_size)
        hash_obj = hashlib.new(self.cs_type)

        pos = start
        while pos < end:
            chunk = os.pread(fd, min(READ_CHUNK_SIZE, end - pos), pos)
            if not chunk:
                raise Error(
                    "unexpected end of image file '%s' at offset %d"
                    % (self.image_path, pos)
                )
            hash_obj.update(chunk)
            pos += len(chunk)

        return hash_obj.hexdigest()

    def _check_range(self, fd, item):
        """Verify one block range, return a result tuple."""
        first, last, chksum = item
        if chksum is None:
            return (first, last, None, None, None)

        calculated = self._hash_range(fd, first, last)
        return (first, last, calculated == chksum, calculated, chksum)

    def _consume_result(self, first, last, ok, calculated, chksum):
        """Update statistics and the failure list with one verification result."""
        size = (last - first + 1) * self.block_size

        if ok is None:
            self.skipped_ranges += 1
            self.skipped_bytes += size
            return

        self.verified_ranges += 1
        self.verified_bytes += size
        if not ok:
            self.failures.append(
                {
                    "first": first,
                    "last": last,
                    "calculated": calculated,
                    "expected": chksum,
                }
            )

    def _iter_results(self, fd):
        """Yield verification results, possibly in parallel."""

        if self.jobs == 1 or len(self.ranges) < 2:
            for item in self.ranges:
                yield self._check_range(fd, item)
            return

        with ThreadPoolExecutor(max_workers=self.jobs) as executor:
            batch_size = max(self.jobs * 4, 1)
            for index in range(0, len(self.ranges), batch_size):
                batch = self.ranges[index : index + batch_size]
                for result in executor.map(
                    lambda item: self._check_range(fd, item), batch
                ):
                    yield result

    def verify(self, progress=None):
        """
        Verify the image file against the bmap file. Returns 'True' if all
        checksums match and 'False' otherwise. The 'progress' argument, if
        specified, is a callback invoked as 'progress(done_bytes, total_bytes)'
        after each verified range.
        """

        self._parse()

        self.verified_ranges = 0
        self.skipped_ranges = 0
        self.verified_bytes = 0
        self.skipped_bytes = 0
        self.failures = []

        total_bytes = sum(
            (last - first + 1) * self.block_size
            for first, last, chksum in self.ranges
            if chksum is not None
        )
        done_bytes = 0

        fd = self._open_image()
        try:
            for first, last, ok, calculated, chksum in self._iter_results(fd):
                self._consume_result(first, last, ok, calculated, chksum)
                if ok is not None:
                    done_bytes += (last - first + 1) * self.block_size
                if progress is not None:
                    progress(done_bytes, total_bytes)
        finally:
            os.close(fd)

        if self.skipped_ranges:
            _log.warning(
                "%d range(s) (%s) have no checksums and were not verified",
                self.skipped_ranges,
                human_size(self.skipped_bytes),
            )

        return not self.failures

    def failure_messages(self):
        """Yield human-readable descriptions of the failed ranges."""
        for failure in self.failures[:_MAX_REPORTED_FAILURES]:
            yield (
                "checksum mismatch for blocks %d-%d: calculated '%s', "
                "should be '%s'"
                % (
                    failure["first"],
                    failure["last"],
                    failure["calculated"],
                    failure["expected"],
                )
            )

        hidden = len(self.failures) - _MAX_REPORTED_FAILURES
        if hidden > 0:
            yield "%d more range(s) failed" % hidden
