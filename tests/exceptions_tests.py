"""
    tests.exceptions
    ~~~~~~~~~~~~~~~~

    Tests for the :mod:`retdec.exceptions` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import unittest

from retdec.exceptions import MissingAPIKeyError


class MissingAPIKeyErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.MissingAPIKeyError`."""

    def test_has_correct_description(self):
        ex = MissingAPIKeyError()
        self.assertIn('API key', str(ex))
        self.assertIn('RETDEC_API_KEY', str(ex))
