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
This module implements the 'bmap-send' command line tool, a small wrapper
around 'scp' and 'ssh' which sends an image file together with its bmap file
to a remote host.

The bmap file must be generated beforehand ('bmaptool create'). Locally it is
expected to be '<image>.bmap'. On the remote side it is stored next to the
image and named '<image>.bmap', so that it can be verified there with
'bmaptool verify <image>.bmap'.

By default the remote copy is not verified: the transfer is only about sending
the data and the bmap file. Use '--verify' to run 'bmaptool verify' on the
remote host after the transfer.
"""

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from xml.etree import ElementTree


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


def _send(args):
    """Send the image and its bmap file to the remote destination."""
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

    if bmap_mtime is not None:
        image_mtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(image))
        )
        if image_mtime != bmap_mtime:
            print(
                "warning: bmap source image mtime is '%s', but '%s' has "
                "mtime '%s'" % (bmap_mtime, image, image_mtime),
                file=sys.stderr,
            )
            if getattr(args, "yes", False):
                print(
                    "continuing because --yes was specified",
                    file=sys.stderr,
                )
            else:
                try:
                    answer = input("The image may have changed. Continue? [y/N] ")
                except EOFError:
                    answer = ""
                if answer.strip().lower() not in ("y", "yes"):
                    raise Error("aborted by user")
    else:
        print(
            "warning: bmap has no source image mtime, cannot detect image "
            "changes",
            file=sys.stderr,
        )

    host, remote_image = _parse_destination(args.destination, image)
    remote_bmap = remote_image + ".bmap"

    scp = ["scp", "-p"]
    ssh = ["ssh"]
    if args.port is not None:
        scp += ["-P", str(args.port)]
        ssh += ["-p", str(args.port)]

    # Send the image first and the bmap second, so that the remote side never
    # sees a bmap which refers to an incomplete image.
    print("sending image to %s:%s" % (host, remote_image), file=sys.stderr)
    _run(scp + ["--", image, "%s:%s" % (host, remote_image)])

    print("sending bmap to %s:%s" % (host, remote_bmap), file=sys.stderr)
    _run(scp + ["--", bmap, "%s:%s" % (host, remote_bmap)])

    if args.verify:
        print("verifying %s on %s" % (remote_bmap, host), file=sys.stderr)
        _run(ssh + [host, "bmaptool verify %s" % shlex.quote(remote_bmap)])

    print("%s:%s" % (host, remote_image))


def main(argv=None):
    """Script entry point."""
    parser = argparse.ArgumentParser(
        prog="bmap-send",
        description="send an image and its bmap file to a remote host",
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

    try:
        _send(args)
    except Error as err:
        print("bmap-send: error: %s" % err, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
