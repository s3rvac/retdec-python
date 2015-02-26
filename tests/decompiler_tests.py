"""
    Tests for the :mod:`retdec.decompiler` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import unittest
from unittest import mock

from retdec.decompiler import Decompilation
from retdec.decompiler import Decompiler
from retdec.file import File
from tests.file_tests import AnyFile
from tests.service_tests import BaseServiceTests


class DecompilerRunDecompilationTests(BaseServiceTests):
    """Tests for :func:`retdec.decompiler.Decompiler.run_decompilation()`."""

    def setUp(self):
        super().setUp()

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
