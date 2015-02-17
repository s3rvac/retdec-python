"""
    tests.decompiler
    ~~~~~~~~~~~~~~~~

    Tests for the :mod:`retdec.decompiler` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import os
import unittest

from retdec.decompiler import Decompiler
from retdec.exceptions import MissingAPIKeyError


class DecompilerTests(unittest.TestCase):
    """Tests for the :class:`retdec.decompiler.Decompiler` class."""

    def test_raises_exception_if_api_key_is_not_given_or_available(self):
        with self.assertRaises(MissingAPIKeyError):
            Decompiler()

    def test_api_key_returns_given_key_if_explicitly_given(self):
        decompiler = Decompiler(api_key='API-KEY')
        self.assertEqual(decompiler.api_key, 'API-KEY')

    def test_api_key_returns_key_from_environment_if_available(self):
        try:
            os.environ['RETDEC_API_KEY'] = 'API-KEY'

            decompiler = Decompiler()

            self.assertEqual(decompiler.api_key, 'API-KEY')
        finally:
            # Restore the original state.
            del os.environ['RETDEC_API_KEY']

    def test_api_url_returns_default_url_when_no_url_was_given(self):
        decompiler = Decompiler(api_key='API-KEY')
        self.assertEqual(decompiler.api_url, 'https://retdec.com/service/api')

    def test_api_url_returns_given_url_if_explicitly_given(self):
        decompiler = Decompiler(api_key='API-KEY', api_url='API-URL')
        self.assertEqual(decompiler.api_url, 'API-URL')

    def test_api_url_returns_url_from_environment_if_available(self):
        try:
            os.environ['RETDEC_API_URL'] = 'API-URL'

            decompiler = Decompiler(api_key='API-KEY')

            self.assertEqual(decompiler.api_url, 'API-URL')
        finally:
            # Restore the original state.
            del os.environ['RETDEC_API_URL']

    def test_api_url_returns_url_without_trailing_slash_if_present(self):
        decompiler = Decompiler(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )
        self.assertEqual(decompiler.api_url, 'https://retdec.com/service/api')
