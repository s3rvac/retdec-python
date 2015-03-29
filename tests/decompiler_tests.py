#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompiler` module."""

import unittest
from unittest import mock

from retdec.decompiler import Decompilation
from retdec.decompiler import DecompilationPhase
from retdec.decompiler import Decompiler
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import InvalidValueError
from retdec.file import File
from tests.file_tests import AnyFile
from tests.resource_tests import ResourceTestsBase
from tests.resource_tests import WithDisabledWaitingInterval
from tests.resource_tests import WithMockedIO
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


class DecompilerRunDecompilationTests(BaseServiceTests):
    """Tests for :func:`retdec.decompiler.Decompiler.run_decompilation()`."""

    def setUp(self):
        super().setUp()

        self.input_file = mock.MagicMock(spec_set=File)

        self.decompiler = Decompiler(api_key='KEY')

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.decompiler.run_decompilation(input_file=self.input_file)

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/decompiler/decompilations',
            self.decompiler.api_key
        )

    def test_mode_is_set_to_c_when_not_given_and_file_name_ends_with_c(self):
        self.input_file.name = 'test.c'

        self.decompiler.run_decompilation(input_file=self.input_file)

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'c',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_mode_is_set_to_bin_when_not_given_and_file_name_does_not_end_with_c(self):
        self.input_file.name = 'test.exe'

        self.decompiler.run_decompilation(input_file=self.input_file)

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'bin',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_generate_archive_is_set_to_false_when_not_given(self):
        self.input_file.name = 'test.exe'

        self.decompiler.run_decompilation(
            input_file=self.input_file
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'bin',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_generate_archive_is_set_to_true_when_given_as_true(self):
        self.input_file.name = 'test.exe'

        self.decompiler.run_decompilation(
            input_file=self.input_file,
            generate_archive=True
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'bin',
                'generate_archive': True
            },
            files={'input': AnyFile()}
        )

    def test_generate_archive_is_set_to_false_when_given_as_false(self):
        self.input_file.name = 'test.exe'

        self.decompiler.run_decompilation(
            input_file=self.input_file,
            generate_archive=False
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'bin',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_raises_exception_when_generate_archive_parameter_is_invalid(self):
        self.input_file.name = 'test.exe'

        with self.assertRaises(InvalidValueError):
            self.decompiler.run_decompilation(
                input_file=self.input_file,
                generate_archive='some data'
            )

    def test_mode_is_used_when_given(self):
        self.decompiler.run_decompilation(
            input_file=self.input_file,
            mode='bin'
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'bin',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_raises_exception_when_mode_is_invalid(self):
        with self.assertRaises(InvalidValueError):
            self.decompiler.run_decompilation(
                input_file=self.input_file,
                mode='xxx'
            )

    def test_file_name_extension_is_case_insensitive_during_mode_detection(self):
        self.input_file.name = 'test.C'

        self.decompiler.run_decompilation(input_file=self.input_file)

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={
                'mode': 'c',
                'generate_archive': False
            },
            files={'input': AnyFile()}
        )

    def test_uses_returned_id_to_initialize_decompilation(self):
        self.conn.send_post_request.return_value = {'id': 'ID'}

        decompilation = self.decompiler.run_decompilation(
            input_file=self.input_file
        )

        self.assertTrue(decompilation.id, 'ID')


class DecompilationPhaseTests(unittest.TestCase):
    """Tests of :class:`retdec.decompiler.DecompilationPhase`."""

    def test_arguments_passed_to_initializer_are_accessible(self):
        phase = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertEqual(phase.name, 'NAME')
        self.assertEqual(phase.part, 'PART')
        self.assertEqual(phase.description, 'DESCRIPTION')
        self.assertEqual(phase.completion, 75)

    def test_two_phases_with_same_data_are_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertEqual(phase1, phase2)

    def test_two_phases_with_different_name_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='OTHER NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_part_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='OTHER PART',
            description='DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_description_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='OTHER DESCRIPTION',
            completion=75
        )

        self.assertNotEqual(phase1, phase2)

    def test_two_phases_with_different_completion_are_not_equal(self):
        phase1 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        phase2 = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=100
        )

        self.assertNotEqual(phase1, phase2)

    def test_repr_returns_correct_value(self):
        phase = DecompilationPhase(
            name='NAME',
            part='PART',
            description='DESCRIPTION',
            completion=75
        )
        self.assertEqual(
            repr(phase),
            ("retdec.decompiler.DecompilationPhase(name='NAME', "
             "part='PART', description='DESCRIPTION', completion=75)")
        )


class DecompilationTestsBase(ResourceTestsBase):
    """Base class of all tests of :class:`retdec.decompiler.Decompilation`."""

    def status_with(self, status):
        """Adds missing keys to the given status and returns it."""
        status = super().status_with(status)
        if 'completion' not in status:
            status['completion'] = 0
        if 'phases' not in status:
            status['phases'] = []
        return status


class DecompilationTests(DecompilationTestsBase):
    """Tests for :class:`retdec.decompiler.Decompilation`."""

    def test_get_completion_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'completion': 20
        })
        d = Decompilation('ID', self.conn)

        completion = d.get_completion()

        self.assertEqual(completion, 20)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_get_phases_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'phases': [
                {
                    'name': 'name1',
                    'part': 'part1',
                    'description': 'description1',
                    'completion': 1
                },
                {
                    'name': 'name2',
                    'part': 'part2',
                    'description': 'description2',
                    'completion': 2
                }
            ]
        })
        d = Decompilation('ID', self.conn)

        phases = d.get_phases()

        self.assertEqual(len(phases), 2)
        self.assertEqual(phases[0].name, 'name1')
        self.assertEqual(phases[1].name, 'name2')
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_repr_returns_correct_value(self):
        d = Decompilation('ID', self.conn)
        self.assertEqual(
            repr(d),
            "<retdec.decompiler.Decompilation id='ID'>"
        )


# WithDisabledWaitingInterval has to be put as the first base class, see its
# description for the reason why.
class DecompilationWaitUntilFinishedTests(WithDisabledWaitingInterval,
                                          DecompilationTestsBase):
    """Tests for :func:`retdec.resource.Decompilation.wait_until_finished()`.
    """

    def test_returns_when_resource_is_finished(self):
        self.conn.send_get_request.return_value = self.status_with({
            'completion': 100,
            'finished': True,
            'succeeded': True
        })
        d = Decompilation('ID', self.conn)

        d.wait_until_finished()

        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_calls_callback_when_resource_finishes(self):
        self.conn.send_get_request.return_value = self.status_with({
            'completion': 100,
            'finished': True,
            'succeeded': True
        })
        d = Decompilation('ID', self.conn)
        callback = mock.Mock()

        d.wait_until_finished(callback)

        callback.assert_called_once_with(d)

    def test_calls_callback_when_resource_status_changes(self):
        self.conn.send_get_request.side_effect = [
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
        d = Decompilation('ID', self.conn)
        callback = mock.Mock()

        d.wait_until_finished(callback)

        self.assertEqual(len(callback.mock_calls), 2)

    def test_raises_exception_by_default_when_resource_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn)

        with self.assertRaises(DecompilationFailedError):
            d.wait_until_finished()

    def test_calls_on_failure_when_it_is_callable(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn)
        on_failure = mock.Mock()

        d.wait_until_finished(on_failure=on_failure)

        on_failure.assert_called_once_with('error message')

    def test_does_not_raise_exception_when_on_failure_is_none(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        d = Decompilation('ID', self.conn)

        d.wait_until_finished(on_failure=None)


# WithMockedIO has to be put as the first base class, see its description for
# the reason why.
class DecompilationGetOutputTests(WithMockedIO, DecompilationTestsBase):
    """Tests for methods that obtain outputs from a
    :class:`retdec.decompilation.Decompilation`.
    """

    def test_get_output_hll_obtains_file_contents(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_file_contents(
            d.get_output_hll,
            '/ID/outputs/hll',
            is_text_file=True
        )

    def test_save_output_hll_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_hll,
            '/ID/outputs/hll',
            directory=None
        )

    def test_save_output_hll_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_hll,
            '/ID/outputs/hll',
            directory='dir'
        )

    def test_get_output_dsm_obtains_file_contents(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_file_contents(
            d.get_output_dsm,
            '/ID/outputs/dsm',
            is_text_file=True
        )

    def test_save_output_dsm_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_dsm,
            '/ID/outputs/dsm',
            directory=None
        )

    def test_save_output_dsm_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_dsm,
            '/ID/outputs/dsm',
            directory='dir'
        )

    def test_save_output_archive_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_archive,
            '/ID/outputs/archive',
            directory=None
        )

    def test_save_output_archive_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_output_archive,
            '/ID/outputs/archive',
            directory='dir'
        )
