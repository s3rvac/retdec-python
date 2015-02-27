#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.exceptions` module."""

import unittest

from retdec.exceptions import APIError
from retdec.exceptions import MissingAPIKeyError


class MissingAPIKeyErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.MissingAPIKeyError`."""

    def test_has_correct_description(self):
        ex = MissingAPIKeyError()
        self.assertIn('API key', str(ex))
        self.assertIn('RETDEC_API_KEY', str(ex))


class APIErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.APIError`."""

    def test_has_correct_attributes(self):
        ex = APIError(401, 'message', 'description')
        self.assertEqual(ex.code, 401)
        self.assertEqual(ex.message, 'message')
        self.assertEqual(ex.description, 'description')

    def test_str_gives_description(self):
        ex = APIError(401, 'message', 'description')
        self.assertEqual(str(ex), 'description')
