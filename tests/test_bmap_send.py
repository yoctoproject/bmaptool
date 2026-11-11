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
import struct
import tempfile
import time
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
        self._write_bmap()

        # Silence the informational messages printed by '_send()'.
        patcher = mock.patch("builtins.print")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _write_bmap(self, mtime=None):
        extra = ""
        if mtime is not None:
            extra = "  <SourceImageMtime> %s </SourceImageMtime>\n" % mtime

        with open(self.bmap, "w") as bmap:
            bmap.write(
                '<?xml version="1.0" ?>\n'
                '<bmap version="2.0">\n'
                "  <ImageSize> %d </ImageSize>\n"
                "  <BlockSize> 4096 </BlockSize>\n"
                "%s"
                "  <BlockMap>\n"
                "    <Range> 0-2047 </Range>\n"
                "  </BlockMap>\n"
                "</bmap>\n" % (IMAGE_SIZE, extra)
            )

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _args(self, **kwargs):
        values = {
            "image": self.image,
            "destination": "user@host:/data/vm.raw",
            "port": None,
            "verify": False,
            "yes": False,
            # The scp-based tests use the full mode explicitly; the sparse
            # tests pass full=False.
            "full": True,
            "zero_holes": False,
            "remote_python": "python3",
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

    def test_load_bmap_info(self):
        """Image size and source mtime must be read from the bmap file."""
        self._write_bmap("2026-11-07 09:30:00")
        size, mtime = BmapSend._load_bmap_info(self.bmap)
        self.assertEqual(size, IMAGE_SIZE)
        self.assertEqual(mtime, "2026-11-07 09:30:00")

    def test_send_mtime_mismatch_abort(self):
        """A changed source mtime must abort when the user answers 'n'."""
        self._write_bmap("2000-01-01 00:00:00")
        with mock.patch.object(BmapSend, "_run") as run, mock.patch(
            "builtins.input", return_value="n"
        ):
            with self.assertRaises(BmapSend.Error):
                BmapSend._send(self._args())
        run.assert_not_called()

    def test_send_mtime_mismatch_continue(self):
        """A changed source mtime must continue when the user answers 'y'."""
        self._write_bmap("2000-01-01 00:00:00")
        with mock.patch.object(BmapSend, "_run") as run, mock.patch(
            "builtins.input", return_value="y"
        ):
            BmapSend._send(self._args())
        self.assertEqual(len(run.call_args_list), 2)

    def test_send_mtime_mismatch_continue_yes(self):
        """'--yes' must skip the mtime prompt."""
        self._write_bmap("2000-01-01 00:00:00")
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args(yes=True))
        self.assertEqual(len(run.call_args_list), 2)

    def test_send_mtime_mismatch_eof(self):
        """EOF on stdin must abort instead of transferring."""
        self._write_bmap("2000-01-01 00:00:00")
        with mock.patch.object(BmapSend, "_run") as run, mock.patch(
            "builtins.input", side_effect=EOFError
        ):
            with self.assertRaises(BmapSend.Error):
                BmapSend._send(self._args())
        run.assert_not_called()

    def test_send_mtime_match(self):
        """A matching source mtime must not prompt."""
        mtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(self.image))
        )
        self._write_bmap(mtime)
        with mock.patch.object(BmapSend, "_run") as run, mock.patch(
            "builtins.input"
        ) as prompt:
            BmapSend._send(self._args())
        prompt.assert_not_called()
        self.assertEqual(len(run.call_args_list), 2)

    def test_send_without_verify(self):
        """By default only the image and the bmap are sent, in that order."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args())

        calls = [call[0][0] for call in run.call_args_list]
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

        calls = [call[0][0] for call in run.call_args_list]
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

        calls = [call[0][0] for call in run.call_args_list]
        self.assertIn("-P", calls[0])
        self.assertIn("2222", calls[0])
        self.assertIn("-p", calls[2])
        self.assertIn("2222", calls[2])

    def test_send_directory_destination(self):
        """A directory destination must get the local file name appended."""
        with mock.patch.object(BmapSend, "_run") as run:
            BmapSend._send(self._args(destination="host:/data/"))

        calls = [call[0][0] for call in run.call_args_list]
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

    def test_load_bmap_ranges(self):
        """Mapped byte ranges must be parsed and clamped to the image size."""
        image_size, ranges = BmapSend._load_bmap_ranges(self.bmap)
        self.assertEqual(image_size, IMAGE_SIZE)
        self.assertEqual(ranges, [(0, IMAGE_SIZE)])

    def test_send_sparse_streams_only_mapped_ranges(self):
        """The default mode must stream mapped ranges over ssh, not scp."""
        fake = _FakeProcess()

        with mock.patch.object(BmapSend, "_run") as run, mock.patch.object(
            BmapSend, "_progress"
        ), mock.patch(
            "shutil.which", return_value="/usr/bin/ssh"
        ), mock.patch(
            "subprocess.Popen", return_value=fake
        ) as popen:
            BmapSend._send(self._args(full=False))

        command = popen.call_args[0][0]
        self.assertEqual(command[0], "ssh")
        self.assertEqual(command[1], "user@host")
        self.assertIn("python3 -c", command[2])
        self.assertIn("vm.raw", command[2])

        data = fake.stdin.data
        self.assertEqual(struct.unpack("!Q", data[:8])[0], 1)
        offset, length = struct.unpack("!QQ", data[8:24])
        self.assertEqual((offset, length), (0, IMAGE_SIZE))
        self.assertEqual(len(data), 24 + IMAGE_SIZE)

        # Only the small bmap file is sent with scp in sparse mode.
        self.assertEqual(len(run.call_args_list), 1)
        self.assertEqual(run.call_args_list[0][0][0][0], "scp")

    def test_send_sparse_zero_holes_and_remote_python(self):
        """--zero-holes and --remote-python must reach the receiver command."""
        fake = _FakeProcess()

        with mock.patch.object(BmapSend, "_run"), mock.patch.object(
            BmapSend, "_progress"
        ), mock.patch(
            "shutil.which", return_value="/usr/bin/ssh"
        ), mock.patch(
            "subprocess.Popen", return_value=fake
        ) as popen:
            BmapSend._send(
                self._args(full=False, zero_holes=True, remote_python="python3.9")
            )

        command = popen.call_args[0][0]
        self.assertIn("python3.9 -c", command[2])
        self.assertTrue(command[2].rstrip().endswith("1"))

    def test_send_sparse_connection_error_message(self):
        """Connection failures must mention ssh, python and the destination."""
        with mock.patch.object(BmapSend, "_run"), mock.patch.object(
            BmapSend, "_progress"
        ), mock.patch(
            "shutil.which", return_value="/usr/bin/ssh"
        ), mock.patch(
            "subprocess.Popen", return_value=_FailingProcess()
        ):
            with self.assertRaises(BmapSend.Error) as context:
                BmapSend._send(self._args(full=False))

        message = str(context.exception)
        self.assertIn("ssh", message)
        self.assertIn("destination path", message)
        self.assertNotIn("needs", message)


class _FakeStdin(object):
    """A writable stdin which keeps the bytes for assertions."""

    def __init__(self):
        self.data = b""

    def write(self, data):
        self.data += data

    def close(self):
        pass


class _FakeProcess(object):
    """A minimal Popen replacement for the sparse transfer tests."""

    def __init__(self):
        self.stdin = _FakeStdin()

    def wait(self):
        return 0

    def kill(self):
        pass


class _FailingStdin(object):
    """A stdin which fails like a closed ssh connection."""

    def write(self, data):
        raise BrokenPipeError("broken pipe")

    def close(self):
        pass


class _FailingProcess(object):
    """A Popen replacement which fails when the sender starts writing."""

    def __init__(self):
        self.stdin = _FailingStdin()

    def wait(self):
        return 1

    def kill(self):
        pass


if __name__ == "__main__":
    unittest.main()
