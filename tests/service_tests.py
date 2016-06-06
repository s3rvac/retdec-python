#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.service` module."""

import os
import unittest

from retdec.conn import APIConnection
from retdec.exceptions import MissingAPIKeyError
from retdec.service import Service
from tests import WithPatching
from tests import mock
from tests.conn_tests import AnyFiles
from tests.conn_tests import AnyParams


class BaseServiceTests(unittest.TestCase, WithPatching):
    """A base class for tests of :class:`retdec.service.Service` subclasses."""

    def setUp(self):
        # Mock APIConnection so that when it is instantiated, it returns our
        # connection that can be used in the tests.
        self.conn = mock.MagicMock(spec_set=APIConnection)
        self.APIConnectionMock = mock.Mock()
        self.APIConnectionMock.return_value = self.conn
        self.patch(
            'retdec.service.APIConnection',
            self.APIConnectionMock
        )

    def assert_post_request_was_sent_with(self, path=None, params=AnyParams(),
                                          files=AnyFiles()):
        """Asserts that a POST request was sent with the given path,
        parameters, and files.

        When `path` is ``None``, it is asserted that no path was given when
        sending the POST request.
        """
        if path is not None:
            self.conn.send_post_request.assert_called_once_with(
                path,
                params=params,
                files=files
            )
        else:
            self.conn.send_post_request.assert_called_once_with(
                params=params,
                files=files
            )


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
