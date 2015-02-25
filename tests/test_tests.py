"""
    Tests for the :mod:`retdec.test` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

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
        self.conn_mock.send_get_request.assert_called_once_with()

    def test_auth_raises_exception_when_authentication_fails(self):
        self.conn_mock.send_get_request.side_effect = AuthenticationError(
            code=401,
            message='Unauthorized by API Key',
            description='API key authentication failed.'
        )
        test = Test(api_key='INVALID-API-KEY')
        with self.assertRaises(AuthenticationError) as cm:
            test.auth()
