#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompiler` module."""

from unittest import mock

from retdec.decompiler import Decompilation
from retdec.decompiler import Decompiler
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import InvalidValueError
from retdec.file import File
from tests.file_tests import AnyFile
from tests.resource_tests import ResourceTestsBase
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

    def test_raises_exception_when_mode_is_invalid(self):
        with self.assertRaises(InvalidValueError):
            self.decompiler.run_decompilation(
                input_file=self.input_file_mock,
                mode='xxx'
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


class DecompilationTestsBase(ResourceTestsBase):
    """Base class for all tests of :class:`retdec.decompiler.Decompilation`."""

    def status_with(self, status):
        """Adds missing keys to the given status and returns it."""
        status = super().status_with(status)
        if 'completion' not in status:
            status['completion'] = 0
        return status


class DecompilationTests(DecompilationTestsBase):
    """Tests for :class:`retdec.decompiler.Decompilation`."""


class DecompilationWaitUntilFinishedTests(DecompilationTestsBase):
    """Tests for :func:`retdec.resource.Decompilation.wait_until_finished()`."""

    def test_returns_when_resource_is_finished(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'completion': 100,
            'finished': True,
            'succeeded': True
        })
        d = Decompilation('ID', self.conn_mock)

        d.wait_until_finished()

        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_calls_callback_when_resource_finishes(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'completion': 100,
            'finished': True,
            'succeeded': True
        })
        d = Decompilation('ID', self.conn_mock)
        callback = mock.Mock()

        d.wait_until_finished(callback)

        callback.assert_called_once_with(d)

    def test_calls_callback_when_resource_status_changes(self):
        self.conn_mock.send_get_request.side_effect = [
            self.status_with({
                'completion': 0,
                'finished': False,
                'succeeded': False
            }), self.status_with({
                'completion': 15,
                'finished': False,
                'succeeded': False
            }), self.status_with({
                'completion': 100,
                'finished': True,
                'succeeded': True
            })
        ]
        d = Decompilation('ID', self.conn_mock)
        callback = mock.Mock()

        d.wait_until_finished(callback)

        self.assertEqual(len(callback.mock_calls), 2)

    def test_raises_exception_by_default_when_resource_failed(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn_mock)

        with self.assertRaises(DecompilationFailedError):
            d.wait_until_finished()

    def test_calls_on_failure_when_it_is_callable(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn_mock)
        on_failure_mock = mock.Mock()

        d.wait_until_finished(on_failure=on_failure_mock)

        on_failure_mock.assert_called_once_with('error message')

    def test_does_not_raise_exception_when_on_failure_is_none(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn_mock)

        d.wait_until_finished(on_failure=None)
