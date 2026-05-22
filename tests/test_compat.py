# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=88 et ai si
#
# Copyright (c) 2012-2014 Intel, Inc.
# License: GPLv2
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
This unit test verifies that the current BmapCopy module can read every
historical bmap file format supplied as a fixture in `tests/test-data/`.
"""

# Disable the following pylint recommendations:
#   *  Too many public methods (R0904)
#   *  Attribute 'XYZ' defined outside __init__ (W0201), because unittest
#      classes are not supposed to have '__init__()'
# pylint: disable=R0904
# pylint: disable=W0201

import os
import shutil
import tempfile
from tests import helpers
from bmaptool import TransRead, BmapCopy

# This is a work-around for Centos 6
try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

# Test image file name
_IMAGE_NAME = "test.image.gz"
# Test bmap file names template
_BMAP_TEMPL = "test.image.bmap.v"
# Name of the subdirectory where test data are stored
_TEST_DATA_SUBDIR = "test-data"


class TestCompat(unittest.TestCase):
    """The test class for this unit test."""

    def test(self):
        """The test entry point."""

        test_data_dir = os.path.join(os.path.dirname(__file__), _TEST_DATA_SUBDIR)
        image_path = os.path.join(test_data_dir, _IMAGE_NAME)

        # Construct the list of bmap files to test
        self._bmap_paths = []
        for dentry in os.listdir(test_data_dir):
            dentry_path = os.path.join(test_data_dir, dentry)
            if os.path.isfile(dentry_path) and dentry.startswith(_BMAP_TEMPL):
                self._bmap_paths.append(dentry_path)

        # Create and open a temporary file for uncompressed image and its copy
        self._f_image = tempfile.NamedTemporaryFile(
            "wb+", prefix=_IMAGE_NAME, suffix=".image"
        )
        self._f_copy = tempfile.NamedTemporaryFile(
            "wb+", prefix=_IMAGE_NAME, suffix=".copy"
        )

        # Uncompress the test image into 'self._f_image'
        f_tmp_img = TransRead.TransRead(image_path)
        shutil.copyfileobj(f_tmp_img, self._f_image)
        f_tmp_img.close()
        self._f_image.flush()

        image_chksum = helpers.calculate_chksum(self._f_image.name)
        image_size = os.path.getsize(self._f_image.name)

        # Test the current version of BmapCopy
        for bmap_path in self._bmap_paths:
            helpers.copy_and_verify_image(
                image_path, self._f_copy.name, bmap_path, image_chksum, image_size
            )

        self._f_copy.close()
        self._f_image.close()
