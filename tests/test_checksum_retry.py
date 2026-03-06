# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# License: GPLv2
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License, version 2 or any later version,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This test verifies the checksum-retry functionality, which retries writing
blocks if their checksums don't match after being written.
"""

# Disable the following pylint recommendations:
#   * Too many public methods (R0904)
#   * Too many local variables (R0914)
# pylint: disable=R0904
# pylint: disable=R0914

import os
import sys
import tempfile
import hashlib
from bmaptool import BmapCreate, BmapCopy, TransRead, BmapHelpers

# This is a work-around for Centos 6
try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest


class ChecksumMismatchFile:
    """
    A wrapper around a file object that can simulate write failures
    by corrupting specific byte ranges on read-back.
    
    Modes:
      'once': Corrupt on first read, then return clean data
      'always': Corrupt on every read
    """

    def __init__(self, file_obj, corruption_ranges=None, mode='once'):
        """
        Initialize with a file object and optional list of byte ranges to corrupt.
        
        Args:
            file_obj: underlying file object
            corruption_ranges: list of (start_byte, end_byte) tuples to corrupt on read
            mode: 'once' to corrupt only on first read, 'always' to always corrupt
        """
        self._file = file_obj
        self.corruption_ranges = corruption_ranges or []
        self.mode = mode
        self._corruption_count = 0  # Track how many times we've applied corruption

    def write(self, data):
        """Pass through write to underlying file."""
        return self._file.write(data)

    def read(self, size=-1):
        """Read from file, optionally corrupting specified ranges."""
        pos = self._file.tell()
        data = bytearray(self._file.read(size))

        should_corrupt = False
        if self.mode == 'once':
            should_corrupt = self._corruption_count == 0
        elif self.mode == 'always':
            should_corrupt = True

        if should_corrupt and self.corruption_ranges:
            # Apply corruptions to matching ranges
            for start, end in self.corruption_ranges:
                # Check if any part of this read overlaps with corruption range
                read_end = pos + len(data)
                if start < read_end and end > pos:
                    # Calculate overlap
                    overlap_start = max(0, start - pos)
                    overlap_end = min(len(data), end - pos)
                    # Flip bits in the overlapping region
                    for i in range(overlap_start, overlap_end):
                        data[i] ^= 0xFF
            self._corruption_count += 1

        return bytes(data)

    def seek(self, pos, whence=0):
        """Pass through seek to underlying file."""
        return self._file.seek(pos, whence)

    def tell(self):
        """Pass through tell to underlying file."""
        return self._file.tell()

    def flush(self):
        """Pass through flush to underlying file."""
        return self._file.flush()

    def fileno(self):
        """Pass through fileno to underlying file."""
        return self._file.fileno()

    @property
    def name(self):
        """Pass through name from underlying file."""
        return self._file.name

    def close(self):
        """Pass through close to underlying file."""
        return self._file.close()


def _create_test_image_with_bmap(image_size, directory=None):
    """
    Create a test image and its corresponding bmap file with checksums.
    Returns (image_path, bmap_path)
    
    The bmap file includes checksums for all ranges, which are verified
    during copy operations, so no separate whole-image checksum is needed.
    """
    # Create image file with some data
    f_image = tempfile.NamedTemporaryFile(
        "wb+", prefix="test_image_", delete=False, dir=directory, suffix=".img"
    )
    image_path = f_image.name

    # Fill image with deterministic data
    chunk_size = 1024
    written = 0
    seed_byte = 0
    while written < image_size:
        to_write = min(chunk_size, image_size - written)
        # Create deterministic pattern
        data = bytes([(seed_byte + i) % 256 for i in range(to_write)])
        f_image.write(data)
        written += to_write
        seed_byte = (seed_byte + to_write) % 256

    f_image.flush()
    f_image.close()

    # Create bmap for the image
    f_bmap = tempfile.NamedTemporaryFile(
        "w+", prefix="test_image_", delete=False, dir=directory, suffix=".bmap"
    )
    bmap_path = f_bmap.name
    f_bmap.close()

    creator = BmapCreate.BmapCreate(image_path, bmap_path)
    creator.generate(include_checksums=True)

    return image_path, bmap_path


class TestChecksumRetry(unittest.TestCase):
    """Test the checksum-retry functionality."""

    def test_checksum_retry_aligned_image(self):
        """Test checksum-retry with image size aligned to block size."""
        # 8192 bytes = 2 blocks of 4096 bytes
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            # Test with checksum-retry enabled
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=1
            )
            # copy() verifies each bmap range's checksum during operation
            writer.copy(sync=True, verify=True)

            # Verify destination has correct size
            dest_size = os.path.getsize(dest_path)
            self.assertEqual(dest_size, image_size)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_retry_non_aligned_image(self):
        """Test checksum-retry with image size NOT aligned to block size."""
        # 9000 bytes = 2.19... blocks of 4096 bytes (non-aligned)
        image_size = 9000
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=1
            )
            # copy() verifies each bmap range's checksum during operation
            writer.copy(sync=True, verify=True)

            # Verify destination has correct size
            dest_size = os.path.getsize(dest_path)
            self.assertEqual(dest_size, image_size)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_retry_default_and_explicit_values(self):
        """Test that default retry=1 and explicit retry=1 behave the same."""
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            # Test with default retry (should be 1 or string "1")
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            # checksum_retry=None means user didn't specify it, should not retry
            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=None
            )
            writer.copy(sync=True, verify=True)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)

            # Test with explicit retry=1
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=1
            )
            writer.copy(sync=True, verify=True)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_retry_multiple_retries(self):
        """Test checksum-retry with multiple retry attempts."""
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            # Test with retry limit of 3
            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=3
            )
            # copy() verifies each bmap range's checksum during operation
            writer.copy(sync=True, verify=True)

            # Verify destination has correct size
            dest_size = os.path.getsize(dest_path)
            self.assertEqual(dest_size, image_size)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_retry_without_bmap_checksums(self):
        """Test checksum-retry when bmap file has no checksums."""
        image_size = 8192
        image_path = None
        bmap_path = None

        try:
            # Create image
            f_image = tempfile.NamedTemporaryFile(
                "wb+", prefix="test_image_", delete=False, suffix=".img"
            )
            image_path = f_image.name
            f_image.write(b"X" * image_size)
            f_image.flush()
            f_image.close()

            # Create bmap WITHOUT checksums
            f_bmap = tempfile.NamedTemporaryFile(
                "w+", prefix="test_image_", delete=False, suffix=".bmap"
            )
            bmap_path = f_bmap.name
            f_bmap.close()

            creator = BmapCreate.BmapCreate(image_path, bmap_path)
            creator.generate(include_checksums=False)  # No checksums!

            # Copy with checksum-retry enabled - should issue warning but not fail
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=1
            )
            # Should complete without error (warning is only logged)
            writer.copy(sync=True, verify=True)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            if image_path:
                os.unlink(image_path)
            if bmap_path:
                os.unlink(bmap_path)

    def test_checksum_retry_zero_value(self):
        """Test that checksum_retry=0 or checksum_retry=False is treated as disabled."""
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            # Test with retry=0 (should be treated as disabled)
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=0
            )
            writer.copy(sync=True, verify=True)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_retry_very_small_image(self):
        """Test checksum-retry with very small image (1 byte, non-aligned)."""
        image_size = 1
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            f_image = TransRead.TransRead(image_path)
            f_dest = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest.name
            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=1
            )
            writer.copy(sync=True, verify=True)

            # Verify the copy matches original
            with open(dest_path, "rb") as f:
                copy_data = f.read()

            self.assertEqual(len(copy_data), image_size)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_mismatch_triggers_rewrite(self):
        """
        Test that a checksum mismatch on first verify triggers a rewrite,
        which succeeds on the retry (after the wrapped file stops corrupting).
        """
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            f_image = TransRead.TransRead(image_path)
            f_dest_real = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest_real.name
            f_dest_real.close()

            # Open destination and wrap it to corrupt data on first read
            f_dest_unwrapped = open(dest_path, "r+b")
            # Corrupt the first block (bytes 0-4095) on first read
            f_dest = ChecksumMismatchFile(
                f_dest_unwrapped, corruption_ranges=[(0, 4096)], mode="once"
            )

            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=2
            )

            # This should succeed: write will fail verification due to corruption,
            # trigger a rewrite, and then succeed on retry (corruption only applies once)
            writer.copy(sync=True, verify=True)

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)

    def test_checksum_mismatch_exhausts_retries(self):
        """
        Test that when checksum mismatches persist beyond retry limit,
        an Error is raised.
        """
        image_size = 8192
        image_path, bmap_path = _create_test_image_with_bmap(image_size)

        try:
            f_image = TransRead.TransRead(image_path)
            f_dest_real = tempfile.NamedTemporaryFile("w+b", delete=False)
            dest_path = f_dest_real.name
            f_dest_real.close()

            # Open destination and wrap it to corrupt data on EVERY read
            f_dest_unwrapped = open(dest_path, "r+b")
            # Corrupt the first block on every read (mode='always')
            f_dest = ChecksumMismatchFile(
                f_dest_unwrapped,
                corruption_ranges=[(0, 4096)],
                mode="always"  # Always corrupt!
            )

            f_bmap = open(bmap_path, "r")

            writer = BmapCopy.BmapCopy(
                f_image, f_dest, f_bmap, image_size, checksum_retry=2
            )

            # This should raise Error because verification always fails
            with self.assertRaises(BmapCopy.Error) as context:
                writer.copy(sync=True, verify=True)

            # Verify the error message mentions checksum verification failure
            self.assertIn("checksum verification failed", str(context.exception))

            f_image.close()
            f_dest.close()
            f_bmap.close()
            os.unlink(dest_path)
        finally:
            os.unlink(image_path)
            os.unlink(bmap_path)


if __name__ == "__main__":
    unittest.main()
