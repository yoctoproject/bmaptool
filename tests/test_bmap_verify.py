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

"""Tests for the 'bmaptool verify' functionality."""

import os
import shutil
import tempfile
import unittest

from bmaptool import BmapCreate, BmapVerify, Filemap

IMAGE_SIZE = BmapCreate.SPLIT_THRESHOLD + 8 * 1024 * 1024  # 72 MiB


class TestBmapVerify(unittest.TestCase):
    """Test image verification against a bmap file."""

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix="bmaptool-verify-")
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

        cls.bmap = os.path.join(cls.tmpdir, "image.raw.bmap")
        creator = BmapCreate.BmapCreate(cls.image, cls.bmap, "sha256", jobs=4)
        creator.generate()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def test_verify_ok(self):
        """A matching image must verify successfully."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=4)
        self.assertTrue(verifier.verify())
        self.assertEqual(verifier.failures, [])
        self.assertEqual(verifier.verified_ranges, 3)
        self.assertEqual(verifier.verified_bytes, IMAGE_SIZE)

    def test_verify_single_job(self):
        """Single-threaded verification must produce the same result."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=1)
        self.assertTrue(verifier.verify())
        self.assertEqual(verifier.verified_ranges, 3)

    def test_verify_detects_corruption(self):
        """A modified image byte must be detected."""
        with open(self.image, "r+b") as image:
            image.seek(0)
            original = image.read(1)
            image.seek(0)
            image.write(bytes([original[0] ^ 0xFF]))

        try:
            verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=4)
            self.assertFalse(verifier.verify())
            self.assertEqual(len(verifier.failures), 1)
            self.assertEqual(verifier.failures[0]["first"], 0)
            self.assertTrue(list(verifier.failure_messages()))
        finally:
            with open(self.image, "r+b") as image:
                image.seek(0)
                image.write(original)

    def test_tampered_bmap_is_rejected(self):
        """A modified bmap checksum must be rejected before data checks."""
        with open(self.bmap, "rb") as bmap:
            data = bmap.read()

        pos = data.find(b'chksum="') + len(b'chksum="')
        replacement = b"0" if data[pos : pos + 1] != b"0" else b"1"
        tampered = data[:pos] + replacement + data[pos + 1 :]

        path = os.path.join(self.tmpdir, "tampered.bmap")
        with open(path, "wb") as bmap:
            bmap.write(tampered)

        verifier = BmapVerify.BmapVerify(path, self.image)
        with self.assertRaises(BmapVerify.Error):
            verifier.verify()

    def test_checksum_type_mismatch(self):
        """An explicitly requested but wrong checksum type must be rejected."""
        verifier = BmapVerify.BmapVerify(
            self.bmap, self.image, chksum_type="sha512"
        )
        with self.assertRaises(BmapVerify.Error):
            verifier.verify()

    def test_bmap_without_checksums(self):
        """A bmap generated with '--no-checksum' cannot be verified."""
        path = os.path.join(self.tmpdir, "nocs.bmap")
        creator = BmapCreate.BmapCreate(self.image, path, "sha256", jobs=1)
        creator.generate(include_checksums=False)

        verifier = BmapVerify.BmapVerify(path, self.image)
        with self.assertRaises(BmapVerify.Error):
            verifier.verify()

    def test_image_too_small(self):
        """A truncated image must be rejected."""
        path = os.path.join(self.tmpdir, "small.raw")
        with open(path, "wb") as image:
            image.truncate(1024)

        verifier = BmapVerify.BmapVerify(self.bmap, path)
        with self.assertRaises(BmapVerify.Error):
            verifier.verify()

    def test_other_checksum_types(self):
        """Verification must work with sha512 and blake2b."""
        for cs_type in ("sha512", "blake2b"):
            bmap_path = os.path.join(self.tmpdir, "image.%s.bmap" % cs_type)
            creator = BmapCreate.BmapCreate(
                self.image, bmap_path, cs_type, jobs=2
            )
            creator.generate()

            verifier = BmapVerify.BmapVerify(bmap_path, self.image, jobs=2)
            self.assertTrue(verifier.verify())


if __name__ == "__main__":
    unittest.main()
