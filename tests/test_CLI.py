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


class TestCLI(unittest.TestCase):
    def test_valid_signature(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v2.0",
                "--bmap-sig",
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

    def test_unknown_signer(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v2.0",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0imposter.asc",
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
                "tests/test-data/signatures/test.image.bmap.v2.0correct.asc",
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

    def test_wrong_signature_uknown_signer(self):
        completed_process = subprocess.run(
            [
                "bmaptool",
                "copy",
                "--bmap",
                "tests/test-data/test.image.bmap.v1.4",
                "--bmap-sig",
                "tests/test-data/signatures/test.image.bmap.v2.0imposter.asc",
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

    def setUp(self):
        try:
            import gpg
        except ImportError:
            self.skipTest("python module 'gpg' missing")

        os.makedirs("tests/test-data/signatures", exist_ok=True)
        for gnupghome, userid in [
            ("tests/test-data/gnupg/", "correct <foo@bar.org>"),
            ("tests/test-data/gnupg2/", "imposter <blub@bla.net>"),
        ]:
            if os.path.exists(gnupghome):
                shutil.rmtree(gnupghome)
            os.makedirs(gnupghome)
            context = gpg.Context(home_dir=gnupghome, armor=True)
            dmkey = context.create_key(
                userid,
                algorithm="rsa3072",
                expires_in=31536000,
                sign=True,
                certify=True,
            )
            for bmapv in ["2.0", "1.4"]:
                testp = "tests/test-data"
                imbn = "test.image.bmap.v"
                with open(f"{testp}/{imbn}{bmapv}", "rb") as bmapf, open(
                    f"{testp}/signatures/{imbn}{bmapv}{userid.split()[0]}.asc",
                    "wb",
                ) as sigf, open(
                    f"{testp}/signatures/{imbn}{bmapv}{userid.split()[0]}.det.asc",
                    "wb",
                ) as detsigf:
                    bmapcontent = bmapf.read()
                    signed_data, result = context.sign(
                        bmapcontent, mode=gpg.constants.sig.mode.DETACH
                    )
                    sigf.write(signed_data)
                    signed_data, result = context.sign(
                        bmapcontent, mode=gpg.constants.sig.mode.CLEAR
                    )
                    detsigf.write(signed_data)
        os.environ["GNUPGHOME"] = "tests/test-data/gnupg/"
        self.tmpfile = tempfile.mkstemp(prefix="testfile_", dir=".")[1]

    def tearDown(self):
        os.unlink(self.tmpfile)
        for gnupghome, userid in [
            ("tests/test-data/gnupg/", "correct <foo@bar.org>"),
            ("tests/test-data/gnupg2/", "imposter <blub@bla.net>"),
        ]:
            shutil.rmtree(gnupghome)
            for bmapv in ["2.0", "1.4"]:
                testp = "tests/test-data"
                imbn = "test.image.bmap.v"
                os.unlink(f"{testp}/signatures/{imbn}{bmapv}{userid.split()[0]}.asc")
                os.unlink(
                    f"{testp}/signatures/{imbn}{bmapv}{userid.split()[0]}.det.asc"
                )
        os.rmdir("tests/test-data/signatures")


if __name__ == "__main__":
    unittest.main()
