"""
    tests.decompiler
    ~~~~~~~~~~~~~~~~

    Tests for the :mod:`retdec.decompiler` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import io
import os
import unittest
from unittest import mock

from retdec.conn import APIConnection
from retdec.decompiler import Decompilation
from retdec.decompiler import Decompiler
from retdec.exceptions import MissingAPIKeyError
from retdec.file import File
from tests.file_tests import AnyFile
from tests.file_tests import AnyFileNamed


class DecompilerInitializationTests(unittest.TestCase):
    """Tests for the initialization part of
    :class:`retdec.decompiler.Decompiler`.
    """

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


class DecompilerRunDecompilationTests(unittest.TestCase):
    """Tests for :func:`retdec.decompiler.Decompiler.run_decompilation()`."""

    def setUp(self):
        # Mock APIConnection so that when it is instantiated, it returns our
        # connection that can be used in the tests.
        self.conn_mock = mock.MagicMock(spec_set=APIConnection)
        self.APIConnectionMock = mock.Mock()
        self.APIConnectionMock.return_value = self.conn_mock
        patcher = mock.patch(
            'retdec.decompiler.APIConnection',
            self.APIConnectionMock
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        self.input_file_mock = mock.MagicMock(spec_set=File)

        self.decompiler = Decompiler(api_key='KEY')

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.decompiler.run_decompilation(input_file=self.input_file_mock)

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/decompiler/decompilations',
            self.decompiler.api_key
        )

    def test_mode_is_set_to_c_when_not_given_and_file_name_ends_with_c(self):
        self.input_file_mock.name = 'test.c'

        self.decompiler.run_decompilation(input_file=self.input_file_mock)

        self.conn_mock.send_post_request.assert_called_once_with(
            '',
            params={'mode': 'c'},
            files={'input': AnyFile()}
        )

    def test_mode_is_set_to_bin_when_not_given_and_file_name_does_not_end_with_c(self):
        self.input_file_mock.name = 'test.exe'

        self.decompiler.run_decompilation(input_file=self.input_file_mock)

        self.conn_mock.send_post_request.assert_called_once_with(
            '',
            params={'mode': 'bin'},
            files={'input': AnyFile()}
        )

    def test_mode_is_used_when_given(self):
        self.decompiler.run_decompilation(
            input_file=self.input_file_mock,
            mode='bin'
        )

        self.conn_mock.send_post_request.assert_called_once_with(
            '',
            params={'mode': 'bin'},
            files={'input': AnyFile()}
        )

    def test_file_name_extension_is_case_insensitive_during_mode_detection(self):
        self.input_file_mock.name = 'test.C'

        self.decompiler.run_decompilation(input_file=self.input_file_mock)

        self.conn_mock.send_post_request.assert_called_once_with(
            '',
            params={'mode': 'c'},
            files={'input': AnyFile()}
        )

    def test_uses_returned_id_to_initialize_decompilation(self):
        self.conn_mock.send_post_request.return_value = {'id': 'ID'}

        decompilation = self.decompiler.run_decompilation(
            input_file=self.input_file_mock
        )

        self.assertTrue(decompilation.id, 'ID')

    def test_repr_returns_correct_value(self):
        self.assertEqual(
            repr(self.decompiler),
            "<Decompiler api_url='https://retdec.com/service/api'>"
        )


class DecompilationTests(unittest.TestCase):
    """Tests for :class:`retdec.decompiler.Decompilation`."""

    def test_id_returns_passed_id(self):
        d = Decompilation('ID', mock.Mock(spec_set=APIConnection))
        self.assertEqual(d.id, 'ID')
