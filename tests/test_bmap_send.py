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

"""Tests for the 'bmap-send' wrapper (without actually using ssh/scp)."""

import argparse
import os
import shutil
import tempfile
import unittest
from unittest import mock

from bmaptool import BmapSend

IMAGE_SIZE = 8 * 1024 * 1024


class TestBmapSend(unittest.TestCase):
    """Test destination parsing and the transfer command construction."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="bmaptool-send-")
        self.image = os.path.join(self.tmpdir, "image.raw")
        with open(self.image, "wb") as image:
            image.truncate(IMAGE_SIZE)

        self.bmap = self.image + ".bmap"
        with open(self.bmap, "w") as bmap:
            bmap.write(
                '<?xml version="1.0" ?>\n'
                '<bmap version="2.0">\n'
                "  <ImageSize> %d </ImageSize>\n"
                "</bmap>\n" % IMAGE_SIZE
            )

        # Silence the informational messages printed by '_send()'.
        patcher = mock.patch("builtins.print")
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _args(self, **kwargs):
        values = {
            "image": self.image,
            "destination": "user@host:/data/vm.raw",
            "port": None,
            "verify": False,
        }
        values.update(kwargs)
        return argparse.Namespace(**values)

    def test_parse_destination(self):
        """A plain 'user@host:path' destination must be split correctly."""
        host, path = BmapSend._parse_destination(
            "user@host:/data/vm.raw", self.image
        )
        self.assertEqual(host, "user@host")
        self.assertEqual(path, "/data/vm.raw")

    def test_parse_directory_destination(self):
        """A destination ending with '/' is treated as a directory."""
        host, path = BmapSend._parse_destination("host:/data/", self.image)
        self.assertEqual(host, "host")
        self.assertEqual(path, "/data/image.raw")

    def test_parse_bad_destination(self):
        """A destination without 'host:' must be rejected."""
        with self.assertRaises(BmapSend.Error):
            BmapSend._parse_destination("/data/vm.raw", self.image)

    def test_load_bmap_image_size(self):
        """The image size must be read from the bmap file."""
        self.assertEqual(BmapSend._load_bmap_image_size(self.bmap), IMAGE_SIZE)

    def test_send_without_verify(self):
        """By default only the image and the bmap are sent, in that order."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args())

        calls = [call.args[0] for call in run.call_args_list]
        self.assertEqual(len(calls), 2)

        self.assertEqual(calls[0][0], "scp")
        self.assertEqual(calls[0][-2], self.image)
        self.assertEqual(calls[0][-1], "user@host:/data/vm.raw")

        self.assertEqual(calls[1][0], "scp")
        self.assertEqual(calls[1][-2], self.bmap)
        self.assertEqual(calls[1][-1], "user@host:/data/vm.raw.bmap")

    def test_send_with_verify(self):
        """'--verify' must run 'bmaptool verify' on the remote host."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args(verify=True))

        calls = [call.args[0] for call in run.call_args_list]
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[2][0], "ssh")
        self.assertEqual(calls[2][1], "user@host")
        self.assertEqual(
            calls[2][2], "bmaptool verify /data/vm.raw.bmap"
        )

    def test_send_port(self):
        """The SSH port must be passed to both scp and ssh."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args(port=2222, verify=True))

        calls = [call.args[0] for call in run.call_args_list]
        self.assertIn("-P", calls[0])
        self.assertIn("2222", calls[0])
        self.assertIn("-p", calls[2])
        self.assertIn("2222", calls[2])

    def test_send_directory_destination(self):
        """A directory destination must get the local file name appended."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args(destination="host:/data/"))

        calls = [call.args[0] for call in run.call_args_list]
        self.assertEqual(calls[0][-1], "host:/data/image.raw")
        self.assertEqual(calls[1][-1], "host:/data/image.raw.bmap")

    def test_missing_bmap(self):
        """The transfer must fail if the bmap file was not generated."""
        os.unlink(self.bmap)
        with self.assertRaises(BmapSend.Error):
            BmapSend._send(self._args())

    def test_missing_image(self):
        """The transfer must fail if the image does not exist."""
        with self.assertRaises(BmapSend.Error):
            BmapSend._send(self._args(image=os.path.join(self.tmpdir, "nope")))

    def test_bmap_size_mismatch(self):
        """The transfer must fail if the bmap does not match the image."""
        with open(self.bmap, "w") as bmap:
            bmap.write(
                '<?xml version="1.0" ?>\n'
                '<bmap version="2.0">\n'
                "  <ImageSize> 1024 </ImageSize>\n"
                "</bmap>\n"
            )

        with self.assertRaises(BmapSend.Error):
            BmapSend._send(self._args())


if __name__ == "__main__":
    unittest.main()
