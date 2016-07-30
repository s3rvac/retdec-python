#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.conn` module."""

import io
import platform
import unittest

import requests
import responses

from retdec.conn import APIConnection
from retdec.exceptions import AuthenticationError
from retdec.exceptions import ConnectionError
from retdec.exceptions import UnknownAPIError
from tests import mock
from tests.matchers import AnyDictWith
from tests.matchers import Anything


class AnyParams(Anything):
    """A matcher that matches any parameters."""


class AnyParamsWith(AnyDictWith):
    """A matcher that matches any parameters that contain the given
    sub-parameters.
    """


class AnyFilesWith(AnyDictWith):
    """A matcher that matches any files that contain the given sub-files.
    """


class AnyFiles(AnyDictWith):
    """A matcher that matches any files."""


class APIConnectionTests(unittest.TestCase):
    """Tests for :class:`retdec.conn.APIConnection`."""

    def setup_responses(self, method=responses.GET,
                        url='https://retdec.com/service/api',
                        body='{}',
                        **kwargs):
        """Sets up the ``responses`` module so that the given response is
        returned for the request.
        """
        responses.add(
            method,
            url,
            body=body,
            **kwargs
        )

    @responses.activate
    def test_send_get_request_sends_get_request(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.method, responses.GET)

    @responses.activate
    def test_send_get_request_sends_request_to_base_url_when_path_is_empty(self):
        self.setup_responses(url='https://retdec.com/service/api')
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request(path='')

        self.assertEqual(
            responses.calls[0].request.url,
            'https://retdec.com/service/api'
        )

    @responses.activate
    def test_send_get_request_sends_request_to_path_when_path_is_nonempty(self):
        self.setup_responses(url='https://retdec.com/service/api/decompiler')
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request(path='/decompiler')

        self.assertEqual(
            responses.calls[0].request.url,
            'https://retdec.com/service/api/decompiler'
        )

    @responses.activate
    def test_send_get_request_sends_correct_authentication_header(self):
        self.setup_responses(url='https://retdec.com/service/api')
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request()

        # http://en.wikipedia.org/wiki/Basic_access_authentication#Client_side
        self.assertEqual(
            responses.calls[0].request.headers['Authorization'],
            'Basic S0VZOg=='  # base64-encoded string "KEY:"
        )

    @responses.activate
    def test_send_get_request_sends_correct_user_agent_header(self):
        self.setup_responses(url='https://retdec.com/service/api')
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request()

        self.assertEqual(
            responses.calls[0].request.headers['User-Agent'],
            'retdec-python/' + platform.system()
        )

    @responses.activate
    def test_send_get_request_includes_given_parameters(self):
        self.setup_responses(url='https://retdec.com/service/api')
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_get_request(params={'key': 'value'})

        self.assertEqual(
            responses.calls[0].request.url,
            'https://retdec.com/service/api?key=value'
        )

    @responses.activate
    def test_send_get_request_returns_json_body_when_request_succeeds(self):
        self.setup_responses(
            url='https://retdec.com/service/api',
            body='{"key": "value"}'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        response = conn.send_get_request()

        self.assertEqual(response, {'key': 'value'})

    @responses.activate
    def test_send_get_request_raises_exception_when_authentication_fails(self):
        self.setup_responses(
            url='https://retdec.com/service/api',
            status=401,
            body='{"code": 401, "message": "failure", "description": "auth failed"}',
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        with self.assertRaises(AuthenticationError):
            conn.send_get_request()

    @responses.activate
    def test_send_get_request_raises_exception_when_api_returns_unknown_error(self):
        self.setup_responses(
            url='https://retdec.com/service/api',
            status=408,
            body=(
                '{"code": 408, "message": "Request Timeout", '
                '"description": "The request timeouted."}'
            ),
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        with self.assertRaises(UnknownAPIError) as cm:
            conn.send_get_request()
        self.assertEqual(cm.exception.code, 408)
        self.assertEqual(cm.exception.message, 'Request Timeout')
        self.assertEqual(cm.exception.description, 'The request timeouted.')

    # For the following test, we need to mock requests.Session, not just
    # requests. The reason is that HTTP requests are sent through a Session
    # instance, not directly through requests.{get,post}().
    @mock.patch('retdec.conn.requests.Session')
    def test_send_get_request_raises_exception_when_there_is_connection_error(
            self, requests_session):
        requests_session.side_effect = requests.exceptions.ConnectionError(
            'Connection refused.'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        with self.assertRaises(ConnectionError) as cm:
            conn.send_get_request()
        self.assertIn('Connection refused.', str(cm.exception))

    @responses.activate
    def test_send_post_request_sends_post_request(self):
        self.setup_responses(
            method=responses.POST,
            url='https://retdec.com/service/api'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_post_request()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.method, responses.POST)

    @responses.activate
    def test_send_post_request_includes_given_parameters(self):
        self.setup_responses(
            method=responses.POST,
            url='https://retdec.com/service/api'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.send_post_request(params={'key': 'value'})

        self.assertEqual(
            responses.calls[0].request.url,
            'https://retdec.com/service/api?key=value'
        )

    @responses.activate
    def test_send_post_request_includes_given_files(self):
        self.setup_responses(
            method=responses.POST,
            url='https://retdec.com/service/api'
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        files = {'input': ('test.c', io.StringIO('main()'))}
        conn.send_post_request(files=files)

        body = str(responses.calls[0].request.body)
        self.assertIn(
            'Content-Disposition: form-data; name="input"; filename="test.c"',
            body
        )
        self.assertIn('main()', body)

    @responses.activate
    def test_get_file_sends_get_request(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api',
            adding_headers={'Content-Disposition': 'filename=test.c'},
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        conn.get_file()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.method, responses.GET)

    @responses.activate
    def test_get_file_returns_file_with_correct_name_and_data(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api',
            body='data',
            adding_headers={
                'Content-Disposition': 'attachment; filename=test.c'
            },
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        file = conn.get_file()

        self.assertEqual(file.name, 'test.c')
        self.assertEqual(file.read(), b'data')

    @responses.activate
    def test_get_file_returns_file_with_correct_name_when_header_has_quotes(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api',
            body='data',
            adding_headers={
                'Content-Disposition': 'attachment; filename="test.c"'
            },
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        file = conn.get_file()

        self.assertEqual(file.name, 'test.c')

    @responses.activate
    def test_get_file_sets_no_name_when_response_does_not_provide_header(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api',
            body='data',
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        file = conn.get_file()

        self.assertIsNone(file.name)

    @responses.activate
    def test_get_file_sets_no_name_when_response_header_does_not_contain_name(self):
        self.setup_responses(
            method=responses.GET,
            url='https://retdec.com/service/api',
            body='data',
            adding_headers={'Content-Disposition': 'attachment'},
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        file = conn.get_file()

        self.assertIsNone(file.name)

    def test_repr_returns_correct_value(self):
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        self.assertEqual(
            repr(conn),
            "<retdec.conn.APIConnection base_url='https://retdec.com/service/api'>"
        )
