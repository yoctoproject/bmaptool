# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
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
Tests for the bmap creation changes: splitting of large mapped ranges,
multi-threaded checksum calculation and checksum type selection.
"""

import os
import shutil
import tempfile
import time
import unittest
from xml.etree import ElementTree

from bmaptool import BmapCreate, Filemap

BLOCK_SIZE = 4096
IMAGE_SIZE = BmapCreate.SPLIT_THRESHOLD + 8 * 1024 * 1024  # 72 MiB


class TestBmapCreate(unittest.TestCase):
    """Test bmap generation with range splitting and multiple jobs."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix="bmaptool-create-")
        cls.image = os.path.join(cls.tmpdir, "image.raw")

        chunk = b"\x00" * (1024 * 1024)
        with open(cls.image, "wb") as image:
            for _ in range(IMAGE_SIZE // len(chunk)):
                image.write(chunk)

        try:
            Filemap.filemap(cls.image)
        except Filemap.ErrorNotSupp as err:
            shutil.rmtree(cls.tmpdir)
            raise unittest.SkipTest("file mapping is not supported: %s" % err)

        cls.image_mtime = time.time() - 3600
        os.utime(cls.image, (cls.image_mtime, cls.image_mtime))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def _create(self, name, jobs=4, chksum_type="sha256"):
        path = os.path.join(self.tmpdir, name)
        creator = BmapCreate.BmapCreate(
            self.image, path, chksum_type, jobs=jobs
        )
        creator.generate()
        return path, creator

    @staticmethod
    def _parse(path):
        root = ElementTree.parse(path).getroot()
        ranges = []
        for elem in root.find("BlockMap").findall("Range"):
            parts = [part.strip() for part in elem.text.strip().split("-", 1)]
            first = int(parts[0])
            last = int(parts[1]) if len(parts) > 1 else first
            ranges.append((first, last, elem.attrib.get("chksum")))
        return root, ranges

    def test_large_range_is_split(self):
        """A 72 MiB mapped range must be split into 32+32+8 MiB ranges."""
        path, creator = self._create("split.bmap")
        _, ranges = self._parse(path)

        self.assertEqual(len(ranges), 3)
        split_blocks = BmapCreate.SPLIT_SIZE // BLOCK_SIZE
        self.assertEqual(ranges[0], (0, split_blocks - 1, ranges[0][2]))
        self.assertEqual(ranges[1][0], split_blocks)
        self.assertEqual(ranges[2][1], IMAGE_SIZE // BLOCK_SIZE - 1)

        for first, last, chksum in ranges:
            self.assertIsNotNone(chksum)
            self.assertLessEqual(
                (last - first + 1) * BLOCK_SIZE, BmapCreate.SPLIT_SIZE
            )

        self.assertEqual(creator.mapped_cnt, IMAGE_SIZE // BLOCK_SIZE)

    def test_small_range_is_not_split(self):
        """Ranges below the threshold must be kept intact."""
        creator = BmapCreate.BmapCreate.__new__(BmapCreate.BmapCreate)
        creator.block_size = BLOCK_SIZE

        threshold_blocks = BmapCreate.SPLIT_THRESHOLD // BLOCK_SIZE
        self.assertEqual(creator._split_range(0, 100), [(0, 100)])
        self.assertEqual(
            creator._split_range(0, threshold_blocks - 2),
            [(0, threshold_blocks - 2)],
        )

        split_width = BmapCreate.SPLIT_SIZE // BLOCK_SIZE
        # Exactly SPLIT_THRESHOLD bytes is split already.
        self.assertEqual(
            creator._split_range(0, threshold_blocks - 1),
            [(0, split_width - 1), (split_width, threshold_blocks - 1)],
        )
        self.assertEqual(
            creator._split_range(0, threshold_blocks),
            [
                (0, split_width - 1),
                (split_width, 2 * split_width - 1),
                (2 * split_width, threshold_blocks),
            ],
        )

    def test_jobs_are_deterministic(self):
        """Single-threaded and multi-threaded output must be identical."""
        path1, _ = self._create("jobs1.bmap", jobs=1)
        path4, _ = self._create("jobs4.bmap", jobs=4)

        with open(path1, "rb") as f1, open(path4, "rb") as f4:
            self.assertEqual(f1.read(), f4.read())

    def test_checksum_types(self):
        """'sha512' and 'blake2b' must be written and used for ranges."""
        for cs_type, length in (("sha512", 128), ("blake2b", 128)):
            path, _ = self._create("type-%s.bmap" % cs_type, chksum_type=cs_type)
            root, ranges = self._parse(path)

            self.assertEqual(
                root.find("ChecksumType").text.strip(), cs_type
            )
            for _, _, chksum in ranges:
                self.assertEqual(len(chksum), length)

    def test_no_checksum_still_splits(self):
        """'include_checksums=False' must still split large ranges."""
        path = os.path.join(self.tmpdir, "nocs.bmap")
        creator = BmapCreate.BmapCreate(self.image, path, "sha256", jobs=4)
        creator.generate(include_checksums=False)

        _, ranges = self._parse(path)
        self.assertEqual(len(ranges), 3)
        for _, _, chksum in ranges:
            self.assertIsNone(chksum)


    def test_source_image_mtime(self):
        """The bmap must record the source image mtime."""
        path, _ = self._create("mtime.bmap")
        root, _ = self._parse(path)

        mtime = root.find("SourceImageMtime").text.strip()
        expected = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(self.image_mtime)
        )
        self.assertEqual(mtime, expected)


if __name__ == "__main__":
    unittest.main()
