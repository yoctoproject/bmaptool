# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# Copyright (c) 2022 Benedikt Wildenhain
# License: GPLv2
# Author: Benedikt Wildenhain <benedikt.wildenhain@hs-bochum.de>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License, version 2 or any later version,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import unittest

import os
import subprocess
import sys
import tempfile
import tests.helpers
import shutil
from dataclasses import dataclass


@dataclass
class Key:
    gnupghome: str
    uid: str
    fpr: str = None


testkeys = {
    "correct": Key("tests/test-data/gnupg", "correct <foo@bar.org>"),
    "unknown": Key("tests/test-data/gnupg2", "unknown <blub@bla.net>"),
}


class TestCLI(unittest.TestCase):
    def test_valid_signature(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v2.0",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0correct.det.asc",
                "tests/test-data/test.image.gz",
                self.tmpfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed_process.returncode, 0)
        self.assertEqual(completed_process.stdout, b"")
        self.assertIn(
            b"successfully verified bmap file signature", completed_process.stderr
        )

    def test_unknown_signer(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v2.0",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0unknown.det.asc",
                "tests/test-data/test.image.gz",
                self.tmpfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed_process.returncode, 1)
        self.assertEqual(completed_process.stdout, b"")
        self.assertIn(b"discovered a BAD GPG signature", completed_process.stderr)

    def test_wrong_signature(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v1.4",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0correct.det.asc",
                "tests/test-data/test.image.gz",
                self.tmpfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed_process.returncode, 1)
        self.assertEqual(completed_process.stdout, b"")
        self.assertIn(b"discovered a BAD GPG signature", completed_process.stderr)

    def test_wrong_signature_unknown_signer(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v1.4",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0unknown.det.asc",
                "tests/test-data/test.image.gz",
                self.tmpfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed_process.returncode, 1)
        self.assertEqual(completed_process.stdout, b"")
        self.assertIn(b"discovered a BAD GPG signature", completed_process.stderr)

    def test_clearsign(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/signatures/test.image.bmap.v2.0correct.asc",
                "tests/test-data/test.image.gz",
                self.tmpfile,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed_process.returncode, 0)
        self.assertEqual(completed_process.stdout, b"")
        self.assertIn(
            b"successfully verified bmap file signature", completed_process.stderr
        )

    def setUp(self):
        try:
            import gpg
        except ImportError:
            self.skipTest("python module 'gpg' missing")

        os.makedirs("tests/test-data/signatures", exist_ok=True)
        for key in testkeys.values():
            if os.path.exists(key.gnupghome):
                shutil.rmtree(key.gnupghome)
            os.makedirs(key.gnupghome)
            context = gpg.Context(home_dir=key.gnupghome)
            dmkey = context.create_key(
                key.uid,
                algorithm="rsa3072",
                expires_in=31536000,
                sign=True,
                certify=True,
            )
            key.fpr = dmkey.fpr
            with open(f"{key.gnupghome}.keyring", "wb") as f:
                f.write(context.key_export_minimal())
            for bmapv in ["2.0", "1.4"]:
                testp = "tests/test-data"
                imbn = "test.image.bmap.v"
                with open(f"{testp}/{imbn}{bmapv}", "rb") as bmapf:
                    bmapcontent = bmapf.read()
                    with open(
                        f"{testp}/signatures/{imbn}{bmapv}{key.uid.split()[0]}.asc",
                        "wb",
                    ) as sigf:
                        signed_data, result = context.sign(
                            bmapcontent, mode=gpg.constants.sig.mode.CLEAR
                        )
                        sigf.write(signed_data)
                        plaintext, sigs = context.verify(signed_data, None)
                    with open(
                        f"{testp}/signatures/{imbn}{bmapv}{key.uid.split()[0]}.det.asc",
                        "wb",
                    ) as detsigf:
                        signed_data, result = context.sign(
                            bmapcontent, mode=gpg.constants.sig.mode.DETACH
                        )
                        detsigf.write(signed_data)

        self.tmpfile = tempfile.mkstemp(prefix="testfile_", dir=".")[1]
        os.environ["GNUPGHOME"] = testkeys["correct"].gnupghome

    def tearDown(self):
        os.unlink(self.tmpfile)
        for key in testkeys.values():
            shutil.rmtree(key.gnupghome)
            os.unlink(f"{key.gnupghome}.keyring")
            for bmapv in ["2.0", "1.4"]:
                testp = "tests/test-data"
                imbn = "test.image.bmap.v"
                os.unlink(f"{testp}/signatures/{imbn}{bmapv}{key.uid.split()[0]}.asc")
                os.unlink(
                    f"{testp}/signatures/{imbn}{bmapv}{key.uid.split()[0]}.det.asc"
                )
        os.rmdir("tests/test-data/signatures")


if __name__ == "__main__":
    unittest.main()
