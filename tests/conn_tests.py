"""
    Tests for the :mod:`retdec.conn` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import io
import unittest

import responses

from retdec.conn import APIConnection


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
            adding_headers={'Content-Disposition': 'filename=test.c'},
            stream=True
        )
        conn = APIConnection('https://retdec.com/service/api', 'KEY')

        file = conn.get_file()

        self.assertEqual(file.name, 'test.c')
        self.assertEqual(file.read(), b'data')
