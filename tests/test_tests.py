#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.test` module."""

from retdec.exceptions import AuthenticationError
from retdec.test import Test
from tests.service_tests import BaseServiceTests


class TestTests(BaseServiceTests):
    """Tests for :class:`retdec.test.Test`."""

    def test_auth_sends_correct_request(self):
        test = Test(api_key='API-KEY')

        test.auth()

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/test/echo',
            'API-KEY'
        )
        self.conn.send_get_request.assert_called_once_with(params={})

    def test_auth_raises_exception_when_authentication_fails(self):
        self.conn.send_get_request.side_effect = AuthenticationError
        test = Test(api_key='INVALID-API-KEY')

        with self.assertRaises(AuthenticationError):
            test.auth()

    def test_echo_sends_correct_request_and_returns_correct_result(self):
        test = Test(api_key='API-KEY')

        result = test.echo(param='value')

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/test/echo',
            'API-KEY'
        )
        self.conn.send_get_request.assert_called_once_with(params={'param': 'value'})
        self.assertEqual(result, self.conn.send_get_request.return_value)

    def test_echo_raises_exception_when_authentication_fails(self):
        self.conn.send_get_request.side_effect = AuthenticationError
        test = Test(api_key='INVALID-API-KEY')

        with self.assertRaises(AuthenticationError):
            test.echo()
