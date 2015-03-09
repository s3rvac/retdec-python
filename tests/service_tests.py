#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.service` module."""

import os
import unittest
from unittest import mock

from retdec.conn import APIConnection
from retdec.service import Service
from retdec.exceptions import MissingAPIKeyError


class BaseServiceTests(unittest.TestCase):
    """A base class for tests of :class:`retdec.service.Service` subclasses."""

    def setUp(self):
        # Mock APIConnection so that when it is instantiated, it returns our
        # connection that can be used in the tests.
        self.conn = mock.MagicMock(spec_set=APIConnection)
        self.APIConnectionMock = mock.Mock()
        self.APIConnectionMock.return_value = self.conn
        patcher = mock.patch(
            'retdec.service.APIConnection',
            self.APIConnectionMock
        )
        patcher.start()
        self.addCleanup(patcher.stop)


class ServiceTests(unittest.TestCase):
    """Tests for :class:`retdec.service.Service`."""

    def test_raises_exception_if_api_key_is_not_given_or_available(self):
        with self.assertRaises(MissingAPIKeyError):
            Service()

    def test_api_key_returns_given_key_if_explicitly_given(self):
        service = Service(api_key='API-KEY')
        self.assertEqual(service.api_key, 'API-KEY')

    def test_api_key_returns_key_from_environment_if_available(self):
        try:
            os.environ['RETDEC_API_KEY'] = 'API-KEY'

            service = Service()

            self.assertEqual(service.api_key, 'API-KEY')
        finally:
            # Restore the original state.
            del os.environ['RETDEC_API_KEY']

    def test_api_url_returns_default_url_when_no_url_was_given(self):
        service = Service(api_key='API-KEY')
        self.assertEqual(service.api_url, 'https://retdec.com/service/api')

    def test_api_url_returns_given_url_if_explicitly_given(self):
        service = Service(api_key='API-KEY', api_url='API-URL')
        self.assertEqual(service.api_url, 'API-URL')

    def test_api_url_returns_url_from_environment_if_available(self):
        try:
            os.environ['RETDEC_API_URL'] = 'API-URL'

            service = Service(api_key='API-KEY')

            self.assertEqual(service.api_url, 'API-URL')
        finally:
            # Restore the original state.
            del os.environ['RETDEC_API_URL']

    def test_api_url_returns_url_without_trailing_slash_if_present(self):
        service = Service(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )
        self.assertEqual(service.api_url, 'https://retdec.com/service/api')

    def test_repr_returns_correct_value(self):
        service = Service(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )
        self.assertEqual(
            repr(service),
            "<Service api_url='https://retdec.com/service/api'>"
        )
