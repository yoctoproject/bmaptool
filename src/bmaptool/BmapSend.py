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
This module implements the 'bmap-send' command line tool.

By default it reads the block ranges listed in the bmap file and sends only
those ranges to the remote host, so holes in a sparse image are never
transferred.  The remote side runs a short Python 3 receiver which writes each
range at its original offset.

The bmap file must be generated beforehand ('bmaptool create'). Locally it is
expected as '<image>.bmap'. On the remote side it is stored next to the image
and named '<image>.bmap', so that it can be verified there with
'bmaptool verify <image>.bmap'.

Use '--full' to fall back to the old behaviour of sending the whole image with
scp.  By default the remote copy is not verified; use '--verify' to run
'bmaptool verify' on the remote host after the transfer.
"""

import argparse
import os
import re
import shlex
import shutil
import struct
import subprocess
import sys
import time
from xml.etree import ElementTree

# Read the local image in 8 MiB chunks and stream them to the receiver.
_CHUNK_SIZE = 8 * 1024 * 1024

# This program runs on the remote side.  It is passed to "python3 -c" and
# writes the received ranges at their original offsets.
_RECEIVER = r'''
import os
import struct
import sys

path = sys.argv[1]
image_size = int(sys.argv[2])
zero_holes = sys.argv[3] == "1"

inp = sys.stdin.buffer


def read_exact(length):
    chunks = []
    while length:
        chunk = inp.read(min(length, 1024 * 1024))
        if not chunk:
            raise SystemExit("bmap-send: unexpected EOF from sender")
        chunks.append(chunk)
        length -= len(chunk)
    return b"".join(chunks)


is_regular = not os.path.exists(path) or os.path.isfile(path)
if is_regular:
    dest = open(path, "w+b")
    os.ftruncate(dest.fileno(), image_size)
else:
    dest = open(path, "r+b")

count = struct.unpack("!Q", read_exact(8))[0]
ranges = []
for _ in range(count):
    offset, length = struct.unpack("!QQ", read_exact(16))
    ranges.append((offset, length))
    dest.seek(offset)
    left = length
    while left:
        chunk = read_exact(min(left, 1024 * 1024))
        dest.write(chunk)
        left -= len(chunk)

# A regular file was just truncated, so its holes already read back as zero.
# A block device may contain stale data in the holes, so optionally overwrite
# them with zeroes (the sender does not transfer the zeroes).
if zero_holes and not is_regular:
    zero = b"\0" * (1024 * 1024)
    position = 0
    for offset, length in sorted(ranges):
        if offset > position:
            dest.seek(position)
            left = offset - position
            while left:
                chunk = zero[:min(left, len(zero))]
                dest.write(chunk)
                left -= len(chunk)
        position = max(position, offset + length)
    if position < image_size:
        dest.seek(position)
        left = image_size - position
        while left:
            chunk = zero[:min(left, len(zero))]
            dest.write(chunk)
            left -= len(chunk)

dest.flush()
try:
    os.fsync(dest.fileno())
except OSError:
    pass
'''


class Error(Exception):
    """A class for all the exceptions raised by this module."""

    pass


def _parse_destination(destination, image_path):
    """
    Split a 'user@host:/path/to/image.raw' destination into the remote host
    and the remote image path. If the remote path ends with '/', it is treated
    as a directory and the local image name is appended to it.
    """

    match = re.match(r"^(?P<host>[^:]+):(?P<path>.+)$", destination)
    if not match:
        raise Error(
            "bad destination '%s': expected 'user@host:/path/to/image.raw'"
            % destination
        )

    host = match.group("host")
    path = match.group("path")

    if path.endswith("/"):
        path = path + os.path.basename(image_path)

    return host, path


def _load_bmap_info(bmap_path):
    """
    Read '<ImageSize>' and '<SourceImageMtime>' from the bmap file. The mtime
    is 'None' for bmap files created by older bmaptool versions.
    """

    image_size = None
    source_mtime = None

    try:
        with open(bmap_path, "rb") as bmap_file:
            for _, elem in ElementTree.iterparse(bmap_file, events=("end",)):
                if elem.tag == "ImageSize":
                    image_size = int(elem.text)
                elif elem.tag == "SourceImageMtime":
                    source_mtime = (elem.text or "").strip()

                elem.clear()

                if image_size is not None and source_mtime is not None:
                    break
    except (OSError, ElementTree.ParseError, TypeError, ValueError) as err:
        raise Error("cannot read bmap file '%s': %s" % (bmap_path, err))

    if image_size is None:
        raise Error("bmap file '%s' has no 'ImageSize' tag" % bmap_path)

    return image_size, source_mtime


def _load_bmap_image_size(bmap_path):
    """Read the '<ImageSize>' value from the bmap file."""
    return _load_bmap_info(bmap_path)[0]


def _load_bmap_ranges(bmap_path):
    """
    Parse '<BlockSize>', '<ImageSize>' and the '<Range>' elements from the
    bmap file. Return '(image_size, ranges)', where each range is an
    '(offset, length)' tuple of bytes, clamped to the image size.
    """

    try:
        tree = ElementTree.parse(bmap_path)
    except (OSError, ElementTree.ParseError) as err:
        raise Error("cannot parse bmap file '%s': %s" % (bmap_path, err))

    root = tree.getroot()
    if root.tag != "bmap":
        raise Error("'%s' is not a bmap file" % bmap_path)

    try:
        block_size = int(root.find("BlockSize").text)
        image_size = int(root.find("ImageSize").text)
    except (AttributeError, TypeError, ValueError) as err:
        raise Error("invalid BlockSize/ImageSize in '%s': %s" % (bmap_path, err))

    if block_size <= 0 or image_size <= 0:
        raise Error("invalid BlockSize/ImageSize in '%s'" % bmap_path)

    block_map = root.find("BlockMap")
    if block_map is None:
        raise Error("bmap file '%s' has no 'BlockMap' element" % bmap_path)

    ranges = []
    for element in block_map.findall("Range"):
        value = (element.text or "").strip()
        if not value:
            continue
        parts = [item.strip() for item in value.split("-", 1)]
        try:
            first = int(parts[0])
            last = int(parts[1]) if len(parts) > 1 else first
        except ValueError:
            raise Error("invalid block range '%s' in '%s'" % (value, bmap_path))

        offset = first * block_size
        end = min((last + 1) * block_size, image_size)
        length = end - offset
        if length > 0:
            ranges.append((offset, length))

    if not ranges:
        raise Error("bmap file '%s' contains no mapped ranges" % bmap_path)

    return image_size, ranges


def _run(command):
    """Run a command and raise 'Error' if it fails."""
    if shutil.which(command[0]) is None:
        raise Error("'%s' is not installed or not in PATH" % command[0])

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as err:
        raise Error(
            "command failed with exit code %d: %s"
            % (err.returncode, " ".join(command))
        )
    except OSError as err:
        raise Error("cannot run '%s': %s" % (command[0], err))


def _check_mtime(image, bmap_mtime, args):
    """Warn and confirm when the bmap was created for an older image."""
    if bmap_mtime is None:
        print(
            "warning: bmap has no source image mtime, cannot detect image "
            "changes",
            file=sys.stderr,
        )
        return

    image_mtime = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(image))
    )
    if image_mtime == bmap_mtime:
        return

    print(
        "warning: bmap source image mtime is '%s', but '%s' has mtime '%s'"
        % (bmap_mtime, image, image_mtime),
        file=sys.stderr,
    )
    if getattr(args, "yes", False):
        print("continuing because --yes was specified", file=sys.stderr)
        return

    try:
        answer = input("The image may have changed. Continue? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() not in ("y", "yes"):
        raise Error("aborted by user")


def _prepare(args):
    """Validate the image and bmap and return the common transfer data."""

    image = args.image
    if not os.path.isfile(image):
        raise Error("image file '%s' does not exist or is not a regular file" % image)

    bmap = image + ".bmap"
    if not os.path.isfile(bmap):
        raise Error(
            "bmap file '%s' not found, run 'bmaptool create %s' first" % (bmap, image)
        )

    image_size = os.path.getsize(image)
    bmap_size, bmap_mtime = _load_bmap_info(bmap)
    if bmap_size != image_size:
        raise Error(
            "bmap file '%s' does not match image '%s': bmap image size is "
            "%d bytes, but the file size is %d bytes; regenerate the bmap"
            % (bmap, image, bmap_size, image_size)
        )

    _check_mtime(image, bmap_mtime, args)
    host, remote_image = _parse_destination(args.destination, image)
    return image, bmap, image_size, host, remote_image


def _scp_command(args, extra=None):
    """Build an scp command with the optional port."""
    command = ["scp", "-p"]
    if args.port is not None:
        command += ["-P", str(args.port)]
    if extra:
        command += extra
    return command


def _ssh_command(args, host, remote_command):
    """Build an ssh command with the optional port."""
    command = ["ssh"]
    if args.port is not None:
        command += ["-p", str(args.port)]
    return command + [host, remote_command]


def _send_full(args):
    """Send the whole image and its bmap with scp (the old behaviour)."""

    image, bmap, _image_size, host, remote_image = _prepare(args)
    remote_bmap = remote_image + ".bmap"

    print("sending image to %s:%s" % (host, remote_image), file=sys.stderr)
    _run(_scp_command(args, ["--", image, "%s:%s" % (host, remote_image)]))

    print("sending bmap to %s:%s" % (host, remote_bmap), file=sys.stderr)
    _run(_scp_command(args, ["--", bmap, "%s:%s" % (host, remote_bmap)]))

    if args.verify:
        print("verifying %s on %s" % (remote_bmap, host), file=sys.stderr)
        _run(_ssh_command(args, host, "bmaptool verify %s" % shlex.quote(remote_bmap)))

    print("%s:%s" % (host, remote_image))


def _progress(sent, total):
    """Write the transfer progress to stderr."""
    percent = 100.0 * sent / total if total else 100.0
    sys.stderr.write(
        "\rbmap-send: %5.1f%% (%d/%d bytes)" % (percent, sent, total)
    )
    sys.stderr.flush()


def _send_sparse(args):
    """Send only the mapped ranges from the bmap file."""

    image, bmap, image_size, host, remote_image = _prepare(args)
    remote_bmap = remote_image + ".bmap"
    _bmap_image_size, ranges = _load_bmap_ranges(bmap)

    if _bmap_image_size != image_size:
        raise Error(
            "bmap '%s' image size %d does not match image size %d"
            % (bmap, _bmap_image_size, image_size)
        )

    remote_command = "%s -c %s %s %d %d" % (
        shlex.quote(args.remote_python),
        shlex.quote(_RECEIVER),
        shlex.quote(remote_image),
        image_size,
        1 if args.zero_holes else 0,
    )
    command = _ssh_command(args, host, remote_command)

    if shutil.which("ssh") is None:
        raise Error("'ssh' is not installed or not in PATH")

    total = sum(length for _offset, length in ranges)
    print(
        "sending %d mapped range(s), %d bytes to %s:%s"
        % (len(ranges), total, host, remote_image),
        file=sys.stderr,
    )

    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
    except OSError as err:
        raise Error("cannot start the remote receiver: %s" % err)

    sent = 0
    try:
        with open(image, "rb") as f_image:
            process.stdin.write(struct.pack("!Q", len(ranges)))
            for offset, length in ranges:
                process.stdin.write(struct.pack("!QQ", offset, length))
                f_image.seek(offset)
                left = length
                while left:
                    chunk = f_image.read(min(left, _CHUNK_SIZE))
                    if not chunk:
                        raise Error(
                            "unexpected EOF in image '%s' at offset %d"
                            % (image, offset + length - left)
                        )
                    process.stdin.write(chunk)
                    left -= len(chunk)
                    sent += len(chunk)
                    _progress(sent, total)
        process.stdin.close()
    except (BrokenPipeError, OSError):
        process.kill()
        process.wait()
        raise Error(
            "remote receiver failed; it needs '%s' on the remote host "
            "(use --full to fall back to scp)" % args.remote_python
        )

    sys.stderr.write("\n")
    returncode = process.wait()
    if returncode != 0:
        raise Error("remote receiver failed with exit code %d" % returncode)

    print("sending bmap to %s:%s" % (host, remote_bmap), file=sys.stderr)
    _run(_scp_command(args, ["--", bmap, "%s:%s" % (host, remote_bmap)]))

    if args.verify:
        print("verifying %s on %s" % (remote_bmap, host), file=sys.stderr)
        _run(_ssh_command(args, host, "bmaptool verify %s" % shlex.quote(remote_bmap)))

    print("%s:%s" % (host, remote_image))


def _send(args):
    """Send the image and its bmap file to the remote destination."""
    if getattr(args, "full", False):
        _send_full(args)
    else:
        _send_sparse(args)


def main(argv=None):
    """Script entry point."""
    parser = argparse.ArgumentParser(
        prog="bmap-send",
        description="send only the mapped blocks of an image to a remote host "
        "(use --full to send the whole image with scp)",
    )

    parser.add_argument("image", help="the local image file")
    parser.add_argument(
        "destination",
        help="the remote destination, e.g. 'user@host:/path/to/image.raw'",
    )
    parser.add_argument("-P", "--port", type=int, help="the SSH port to use")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="continue without prompting when the source image mtime differs",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="send the whole image with scp instead of only the mapped ranges",
    )
    parser.add_argument(
        "--zero-holes",
        action="store_true",
        help="write zeroes to holes when the destination is a block device "
        "(the zeroes are generated remotely, not transferred)",
    )
    parser.add_argument(
        "--remote-python",
        default="python3",
        help="Python 3 interpreter on the remote host (default: python3)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--verify",
        dest="verify",
        action="store_true",
        help="run 'bmaptool verify' on the remote host after the transfer",
    )
    group.add_argument(
        "--no-verify",
        dest="verify",
        action="store_false",
        help="do not verify the image on the remote host (default)",
    )
    parser.set_defaults(verify=False)

    args = parser.parse_args(argv)

    if args.full and args.zero_holes:
        parser.error("--zero-holes cannot be used together with --full")

    try:
        _send(args)
    except Error as err:
        print("bmap-send: error: %s" % err, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
