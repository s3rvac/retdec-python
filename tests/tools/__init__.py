"""
    Tests for the :mod:`retdec.tools` package.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import io
import unittest
from unittest import mock


class ParseArgsBaseTests(unittest.TestCase):
    """Base class for all ``parse_args()`` tests."""

    def setUp(self):
        # Patch sys.stderr (argparse prints error messages to it).
        self.stderr = io.StringIO()
        patcher = mock.patch('sys.stderr', self.stderr)
        patcher.start()
        self.addCleanup(patcher.stop)
