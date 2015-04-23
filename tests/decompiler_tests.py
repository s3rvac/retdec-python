#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompiler` module."""

from retdec.decompiler import Decompiler
from retdec.exceptions import InvalidValueError
from retdec.file import File
from tests import mock
from tests.conn_tests import AnyFilesWith
from tests.conn_tests import AnyParamsWith
from tests.file_tests import AnyFileNamed
from tests.service_tests import BaseServiceTests


class DecompilerTests(BaseServiceTests):
    """Tests for :class:`retdec.decompiler.Decompiler`."""

    def test_repr_returns_correct_value(self):
        decompiler = Decompiler(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )
        self.assertEqual(
            repr(decompiler),
            "<retdec.decompiler.Decompiler api_url='https://retdec.com/service/api'>"
        )


class DecompilerStartDecompilationTests(BaseServiceTests):
    """Tests for :func:`retdec.decompiler.Decompiler.start_decompilation()`."""

    def setUp(self):
        super().setUp()

        self.input_file = mock.Mock(spec_set=File)

        self.decompiler = Decompiler(api_key='KEY')

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.decompiler.start_decompilation(input_file=self.input_file)

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/decompiler/decompilations',
            self.decompiler.api_key
        )

    def test_sends_input_file(self):
        self.decompiler.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            files=AnyFilesWith(input=AnyFileNamed(self.input_file.name))
        )

    def test_mode_is_set_to_c_when_not_given_and_file_name_ends_with_c(self):
        self.input_file.name = 'test.c'

        self.decompiler.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='c')
        )

    def test_mode_is_set_to_bin_when_not_given_and_file_name_does_not_end_with_c(self):
        self.input_file.name = 'test.exe'

        self.decompiler.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='bin')
        )

    def test_generate_archive_is_set_to_false_when_not_given(self):
        self.input_file.name = 'test.exe'

        self.decompiler.start_decompilation(
            input_file=self.input_file
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_archive=False)
        )

    def test_generate_archive_is_set_to_true_when_given_as_true(self):
        self.input_file.name = 'test.exe'

        self.decompiler.start_decompilation(
            input_file=self.input_file,
            generate_archive=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_archive=True)
        )

    def test_generate_archive_is_set_to_false_when_given_as_false(self):
        self.input_file.name = 'test.exe'

        self.decompiler.start_decompilation(
            input_file=self.input_file,
            generate_archive=False
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_archive=False)
        )

    def test_raises_exception_when_generate_archive_parameter_is_invalid(self):
        self.input_file.name = 'test.exe'

        with self.assertRaises(InvalidValueError):
            self.decompiler.start_decompilation(
                input_file=self.input_file,
                generate_archive='some data'
            )

    def test_mode_is_used_when_given(self):
        self.decompiler.start_decompilation(
            input_file=self.input_file,
            mode='bin'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='bin')
        )

    def test_raises_exception_when_mode_is_invalid(self):
        with self.assertRaises(InvalidValueError):
            self.decompiler.start_decompilation(
                input_file=self.input_file,
                mode='xxx'
            )

    def test_file_name_extension_is_case_insensitive_during_mode_detection(self):
        self.input_file.name = 'test.C'

        self.decompiler.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='c')
        )

    def test_uses_returned_id_to_initialize_decompilation(self):
        self.conn.send_post_request.return_value = {'id': 'ID'}

        decompilation = self.decompiler.start_decompilation(
            input_file=self.input_file
        )

        self.assertTrue(decompilation.id, 'ID')
