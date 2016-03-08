#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools` package."""

import io
import unittest

from tests import WithPatching


class ToolTestsBase(unittest.TestCase, WithPatching):
    """Base class for tests of tools."""

    def setUp(self):
        super().setUp()

        self.stdout = io.StringIO()
        self.patch('sys.stdout', self.stdout)

        self.stderr = io.StringIO()
        self.patch('sys.stderr', self.stderr)
