#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools` package."""

import io
import unittest
from unittest import mock


class ToolTestsBase(unittest.TestCase):
    """Base class for tests of tools."""

    def setUp(self):
        super().setUp()

        # Patch sys.stdout.
        self.stdout = io.StringIO()
        patcher = mock.patch('sys.stdout', self.stdout)
        patcher.start()
        self.addCleanup(patcher.stop)

        # Patch sys.stderr.
        self.stderr = io.StringIO()
        patcher = mock.patch('sys.stderr', self.stderr)
        patcher.start()
        self.addCleanup(patcher.stop)
