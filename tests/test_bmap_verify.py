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
import subprocess
import tempfile
import time
import unittest
from unittest import mock

from bmaptool import BmapCreate, BmapVerify, CLI, Filemap

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
        cls.image_mtime = time.time() - 3600
        os.utime(cls.image, (cls.image_mtime, cls.image_mtime))
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

    def test_verify_mtime_warning(self):
        """A changed image mtime must warn but not fail verification."""
        original = self.image_mtime
        try:
            os.utime(self.image, (original - 86400, original - 86400))
            verifier = BmapVerify.BmapVerify(self.bmap, self.image)
            with self.assertLogs("bmaptool.BmapVerify", level="WARNING") as logs:
                self.assertTrue(verifier.verify())
            self.assertTrue(any("mtime" in line for line in logs.output))
        finally:
            os.utime(self.image, (original, original))

    def test_verify_single_job(self):
        """Single-threaded verification must produce the same result."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=1)
        self.assertTrue(verifier.verify())
        self.assertEqual(verifier.verified_ranges, 3)

    def test_verify_detects_corruption(self):
        """A modified image byte must be detected."""
        original_mtime = self.image_mtime
        with open(self.image, "r+b") as image:
            image.seek(0)
            original = image.read(1)
            image.seek(0)
            image.write(bytes([original[0] ^ 0xFF]))

        try:
            verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=4)
            with mock.patch("bmaptool.BmapVerify._log"):
                self.assertFalse(verifier.verify())
            self.assertEqual(len(verifier.failures), 1)
            self.assertEqual(verifier.failures[0]["first"], 0)
            self.assertTrue(list(verifier.failure_messages()))
        finally:
            with open(self.image, "r+b") as image:
                image.seek(0)
                image.write(original)
            os.utime(self.image, (original_mtime, original_mtime))

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

    def test_repair_scripts_repair_image(self):
        """The generated scripts must repair the image end to end."""
        good = os.path.join(self.tmpdir, "good.raw")
        shutil.copyfile(self.image, good)
        original_mtime = self.image_mtime

        try:
            with open(self.image, "r+b") as image:
                for offset in (0, 32 * 1024 * 1024, 64 * 1024 * 1024):
                    image.seek(offset)
                    original = image.read(1)
                    image.seek(offset)
                    image.write(bytes([original[0] ^ 0xFF]))

            verifier = BmapVerify.BmapVerify(self.bmap, self.image, jobs=4)
            with mock.patch("bmaptool.BmapVerify._log"):
                self.assertFalse(verifier.verify())
            self.assertEqual(len(verifier.failures), 3)

            bin_path = good + "_retransfer.bin"
            source_text, dest_text, total_size, included, hidden = (
                verifier.repair_scripts(source_image=good, bin_path=bin_path)
            )
            self.assertEqual(total_size, IMAGE_SIZE)
            self.assertEqual(included, 3)
            self.assertEqual(hidden, 0)
            self.assertIn("SOURCE_IMAGE=%s" % good, source_text)
            self.assertIn('dd if="$SOURCE_IMAGE"', source_text)
            self.assertIn("bs=%d" % verifier.block_size, source_text)
            self.assertIn("EXPECTED_SIZE=%d" % IMAGE_SIZE, dest_text)
            self.assertIn("conv=notrunc", dest_text)
            self.assertIn("bmaptool verify", dest_text)

            source_path = os.path.join(self.tmpdir, "source.sh")
            dest_path = os.path.join(self.tmpdir, "dest.sh")
            with open(source_path, "w") as script:
                script.write(source_text)
            with open(dest_path, "w") as script:
                script.write(dest_text)

            subprocess.run(
                ["sh", source_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertEqual(os.path.getsize(bin_path), IMAGE_SIZE)
            self.assertTrue(os.path.exists(bin_path + ".sha256"))

            subprocess.run(
                ["sh", dest_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            repaired = BmapVerify.BmapVerify(self.bmap, self.image, jobs=4)
            with mock.patch("bmaptool.BmapVerify._log"):
                self.assertTrue(repaired.verify())
        finally:
            shutil.copyfile(good, self.image)
            os.utime(self.image, (original_mtime, original_mtime))

    def test_repair_non_block_aligned_image(self):
        """A trailing partial block must survive verify and repair."""
        size = 8 * 1024 * 1024 + 123
        image = os.path.join(self.tmpdir, "unaligned.raw")
        good = os.path.join(self.tmpdir, "unaligned-good.raw")

        with open(image, "wb") as image_file:
            image_file.write(b"\x00" * size)
        shutil.copyfile(image, good)

        bmap = image + ".bmap"
        creator = BmapCreate.BmapCreate(image, bmap, "sha256", jobs=2)
        creator.generate()

        with open(image, "r+b") as image_file:
            image_file.seek(size - 1)
            original = image_file.read(1)
            image_file.seek(size - 1)
            image_file.write(bytes([original[0] ^ 0xFF]))

        verifier = BmapVerify.BmapVerify(bmap, image)
        with mock.patch("bmaptool.BmapVerify._log"):
            self.assertFalse(verifier.verify())

        bin_path = good + "_retransfer.bin"
        source_text, dest_text, total_size, included, hidden = (
            verifier.repair_scripts(source_image=good, bin_path=bin_path)
        )
        self.assertEqual(total_size, size)
        self.assertEqual(included, 1)
        self.assertEqual(hidden, 0)

        source_path = os.path.join(self.tmpdir, "source-unaligned.sh")
        dest_path = os.path.join(self.tmpdir, "dest-unaligned.sh")
        with open(source_path, "w") as script:
            script.write(source_text)
        with open(dest_path, "w") as script:
            script.write(dest_text)

        subprocess.run(
            ["sh", source_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertEqual(os.path.getsize(bin_path), size)

        subprocess.run(
            ["sh", dest_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        repaired = BmapVerify.BmapVerify(bmap, image)
        with mock.patch("bmaptool.BmapVerify._log"):
            self.assertTrue(repaired.verify())

    def test_repair_scripts_have_expected_commands(self):
        """The scripts must use cumulative bin offsets and target blocks."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image)
        verifier._parse()
        verifier.failures = [
            {
                "first": 0,
                "last": 8191,
                "calculated": "0" * 64,
                "expected": "1" * 64,
            },
            {
                "first": 8192,
                "last": 16383,
                "calculated": "0" * 64,
                "expected": "1" * 64,
            },
        ]

        source_text, dest_text, total_size, included, hidden = (
            verifier.repair_scripts(
                source_image="/data/good.raw",
                bin_path="/tmp/vm.raw_retransfer.bin",
            )
        )
        self.assertEqual(total_size, 64 * 1024 * 1024)
        self.assertEqual(included, 2)
        self.assertEqual(hidden, 0)
        self.assertIn("SOURCE_IMAGE=/data/good.raw", source_text)
        self.assertIn("skip=0 count=8192", source_text)
        self.assertIn("skip=8192 count=8192", source_text)
        self.assertIn('skip=0 count=8192 of="$IMAGE" seek=0', dest_text)
        self.assertIn(
            'skip=8192 count=8192 of="$IMAGE" seek=8192', dest_text
        )
        self.assertIn("EXPECTED_SIZE=%d" % (64 * 1024 * 1024), dest_text)

    def test_repair_scripts_unknown_checksum_type(self):
        """Unknown checksum types must not produce bogus shell commands."""
        bmap_path = os.path.join(self.tmpdir, "sha3.bmap")
        creator = BmapCreate.BmapCreate(
            self.image, bmap_path, "sha3_256", jobs=2
        )
        creator.generate()

        verifier = BmapVerify.BmapVerify(bmap_path, self.image)
        verifier._parse()
        verifier.failures = [
            {
                "first": 0,
                "last": 8191,
                "calculated": "0" * 64,
                "expected": "1" * 64,
            }
        ]

        with self.assertRaises(BmapVerify.Error):
            verifier.repair_scripts()

    def test_repair_scripts_hidden_warning(self):
        """Failed ranges beyond the limit must be called out."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image)
        verifier._parse()
        verifier.failures = [
            {
                "first": i,
                "last": i,
                "calculated": "0" * 64,
                "expected": "1" * 64,
            }
            for i in range(BmapVerify._MAX_REPAIR_RANGES + 1)
        ]

        source_text, dest_text, total_size, included, hidden = (
            verifier.repair_scripts()
        )
        self.assertEqual(included, BmapVerify._MAX_REPAIR_RANGES)
        self.assertEqual(hidden, 1)
        self.assertIn("WARNING: only 1000 of 1001", source_text)
        self.assertIn("additional failed range(s)", dest_text)

    def test_write_repair_scripts(self):
        """The CLI must write executable scripts to the temp directory."""
        verifier = BmapVerify.BmapVerify(self.bmap, self.image)
        verifier._parse()
        verifier.failures = [
            {
                "first": i * 1024,
                "last": i * 1024 + 1023,
                "calculated": "0" * 64,
                "expected": "1" * 64,
            }
            for i in range(7)
        ]

        source_path = os.path.join(self.tmpdir, "source_image.raw.sh")
        dest_path = os.path.join(self.tmpdir, "dest_repair_image.raw.sh")
        for path in (source_path, dest_path):
            if os.path.exists(path):
                os.unlink(path)

        try:
            with mock.patch("bmaptool.CLI.log"), mock.patch(
                "bmaptool.CLI.tempfile.gettempdir", return_value=self.tmpdir
            ):
                CLI._write_repair_scripts(verifier, "/tmp/good.raw")

            for path in (source_path, dest_path):
                self.assertTrue(os.path.exists(path))
                self.assertTrue(os.access(path, os.X_OK))

            with open(source_path) as script:
                source_text = script.read()
            with open(dest_path) as script:
                dest_text = script.read()

            self.assertIn("SOURCE_IMAGE=/tmp/good.raw", source_text)
            self.assertIn("EXPECTED_SIZE=", dest_text)
            self.assertIn("bmaptool verify", dest_text)
        finally:
            for path in (source_path, dest_path):
                if os.path.exists(path):
                    os.unlink(path)


if __name__ == "__main__":
    unittest.main()
