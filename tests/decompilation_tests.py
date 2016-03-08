#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompilation` module."""

from retdec.decompilation import Decompilation
from retdec.exceptions import ArchiveGenerationFailedError
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import OutputNotRequestedError
from tests import mock
from tests.resource_tests import ResourceTestsBase
from tests.resource_tests import WithDisabledWaitingInterval
from tests.resource_tests import WithMockedIO


class DecompilationTestsBase(ResourceTestsBase):
    """Base class of all tests of :class:`retdec.decompilation.Decompilation`.
    """

    def status_with(self, status):
        """Adds missing keys to the given status and returns it."""
        status = super().status_with(status)
        if 'completion' not in status:
            status['completion'] = 0
        if 'phases' not in status:
            status['phases'] = []
        return status


class DecompilationTests(DecompilationTestsBase):
    """Tests for :class:`retdec.decompilation.Decompilation`."""

    def get_decompilation_that_did_not_request_archive_to_be_generated(self):
        # This is signalized by a response that does not include the 'archive'
        # key.
        self.conn.send_get_request.return_value = self.status_with({})
        return Decompilation('ID', self.conn)

    def test_get_completion_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'completion': 20
        })
        d = Decompilation('ID', self.conn)

        completion = d.get_completion()

        self.assertEqual(completion, 20)
        self.assert_get_request_was_sent_with('/ID/status')

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
        self.assert_get_request_was_sent_with('/ID/status')

    def test_get_phases_ignores_unknown_phase_attributes(self):
        self.conn.send_get_request.return_value = self.status_with({
            'phases': [
                {
                    'name': 'name',
                    'part': 'part',
                    'description': 'description',
                    'completion': 0,
                    'unknown_attr': None  # This attribute is to be ignored.
                }
            ]
        })
        d = Decompilation('ID', self.conn)

        phases = d.get_phases()

        self.assertEqual(len(phases), 1)
        self.assertFalse(hasattr(phases[0], 'unknown_attr'))

    def test_archive_generation_has_finished_checks_status_on_first_call(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        d.archive_generation_has_finished()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_archive_generation_has_finished_returns_true_when_generated(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertTrue(d.archive_generation_has_finished())

    def test_archive_generation_has_finished_returns_true_when_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertTrue(d.archive_generation_has_finished())

    def test_archive_generation_has_finished_returns_false_when_not_finished(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertFalse(d.archive_generation_has_finished())

    def test_archive_generation_has_finished_raises_exception_when_archive_not_requested(self):
        d = self.get_decompilation_that_did_not_request_archive_to_be_generated()

        with self.assertRaises(OutputNotRequestedError):
            d.archive_generation_has_finished()

    def test_archive_generation_has_succeeded_checks_status_on_first_call(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        d.archive_generation_has_succeeded()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_archive_generation_has_succeeded_returns_true_when_succeeded(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertTrue(d.archive_generation_has_succeeded())

    def test_archive_generation_has_succeeded_returns_false_when_not_finished(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertFalse(d.archive_generation_has_succeeded())

    def test_archive_generation_has_succeeded_returns_false_when_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertFalse(d.archive_generation_has_succeeded())

    def test_archive_generation_has_succeeded_raises_exception_when_archive_not_requested(self):
        d = self.get_decompilation_that_did_not_request_archive_to_be_generated()

        with self.assertRaises(OutputNotRequestedError):
            d.archive_generation_has_succeeded()

    def test_archive_generation_has_failed_checks_status_on_first_call(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        d.archive_generation_has_failed()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_archive_generation_has_failed_returns_true_when_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertTrue(d.archive_generation_has_failed())

    def test_archive_generation_has_failed_returns_false_when_succeeded(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertFalse(d.archive_generation_has_failed())

    def test_archive_generation_has_failed_returns_false_when_not_finished(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertFalse(d.archive_generation_has_failed())

    def test_archive_generation_has_failed_raises_exception_when_archive_not_requested(self):
        d = self.get_decompilation_that_did_not_request_archive_to_be_generated()

        with self.assertRaises(OutputNotRequestedError):
            d.archive_generation_has_failed()

    def test_get_archive_error_checks_status_on_first_call(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        d.get_archive_generation_error()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_get_archive_generation_error_returns_none_when_succeeded(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertIsNone(d.get_archive_generation_error())

    def test_get_archive_generation_error_returns_correct_error_when_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        self.assertEqual(d.get_archive_generation_error(), 'error message')

    def test_get_archive_generation_error_raises_exception_when_archive_not_requested(self):
        d = self.get_decompilation_that_did_not_request_archive_to_be_generated()

        with self.assertRaises(OutputNotRequestedError):
            d.get_archive_generation_error()

    def test_repr_returns_correct_value(self):
        d = Decompilation('ID', self.conn)
        self.assertEqual(
            repr(d),
            "<retdec.decompilation.Decompilation id='ID'>"
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

        self.assert_get_request_was_sent_with('/ID/status')

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

        with self.assertRaises(DecompilationFailedError) as cm:
            d.wait_until_finished()
        self.assertRegex(str(cm.exception), r'.*error message.*')

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


# WithDisabledWaitingInterval has to be put as the first base class, see its
# description for the reason why.
class DecompilationWaitUntilArchiveIsGeneratedTests(WithDisabledWaitingInterval,
                                                    DecompilationTestsBase):
    """Tests for
    :class:`retdec.decompilation.Decompilation.wait_until_archive_is_generated()`.
    """

    def test_returns_when_archive_is_generated(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': True,
                'failed': False,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        d.wait_until_archive_is_generated()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_waits_until_archive_is_generated(self):
        self.conn.send_get_request.side_effect = [
            self.status_with({
                'archive': {
                    'generated': False,
                    'failed': False,
                    'error': None
                }
            }), self.status_with({
                'archive': {
                    'generated': True,
                    'failed': False,
                    'error': None
                }
            })
        ]
        d = Decompilation('ID', self.conn)

        d.wait_until_archive_is_generated()

        self.assertEqual(len(self.conn.send_get_request.mock_calls), 2)

    def test_raises_exception_by_default_when_generation_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)

        with self.assertRaises(ArchiveGenerationFailedError) as cm:
            d.wait_until_archive_is_generated()
        self.assertRegex(str(cm.exception), r'.*error message.*')

    def test_calls_on_failure_when_it_is_callable(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': 'error message'
            }
        })
        d = Decompilation('ID', self.conn)
        on_failure = mock.Mock()

        d.wait_until_archive_is_generated(on_failure=on_failure)

        on_failure.assert_called_once_with('error message')

    def test_does_not_raise_exception_when_on_failure_is_none(self):
        self.conn.send_get_request.return_value = self.status_with({
            'archive': {
                'generated': False,
                'failed': True,
                'error': None
            }
        })
        d = Decompilation('ID', self.conn)

        d.wait_until_archive_is_generated(on_failure=None)


# WithMockedIO has to be put as the first base class, see its description for
# the reason why.
class DecompilationGetOutputsTests(WithMockedIO, DecompilationTestsBase):
    """Tests for methods that obtain outputs from a
    :class:`retdec.decompilation.Decompilation`.
    """

    def test_get_hll_code_obtains_file_contents(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_file_contents(
            d.get_hll_code,
            '/ID/outputs/hll',
            is_text_file=True
        )

    def test_save_hll_code_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_hll_code,
            '/ID/outputs/hll',
            directory=None
        )

    def test_save_hll_code_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_hll_code,
            '/ID/outputs/hll',
            directory='dir'
        )

    def test_get_dsm_code_obtains_file_contents(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_file_contents(
            d.get_dsm_code,
            '/ID/outputs/dsm',
            is_text_file=True
        )

    def test_save_dsm_code_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_dsm_code,
            '/ID/outputs/dsm',
            directory=None
        )

    def test_save_dsm_code_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_dsm_code,
            '/ID/outputs/dsm',
            directory='dir'
        )

    def test_save_archive_stores_file_to_cwd_when_directory_is_not_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_archive,
            '/ID/outputs/archive',
            directory=None
        )

    def test_save_archive_stores_file_to_directory_when_given(self):
        d = Decompilation('ID', self.conn)
        self.assert_obtains_and_saves_file(
            d.save_archive,
            '/ID/outputs/archive',
            directory='dir'
        )
