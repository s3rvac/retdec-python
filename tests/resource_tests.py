#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.resource` module."""

import unittest
from unittest import mock

from retdec.conn import APIConnection
from retdec.resource import Resource


class ResourceTestsBase(unittest.TestCase):
    """Base class for tests of :class:`retdec.resource.Resource` and its
    subclasses.
    """

    def setUp(self):
        self.conn_mock = mock.Mock(spec_set=APIConnection)

        # Patch time.sleep() to prevent sleeping during tests.
        self.time_sleep_mock = mock.Mock()
        patcher = mock.patch('time.sleep', self.time_sleep_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def status_with(self, status):
        """Adds missing keys to the given status and returns it."""
        if 'pending' not in status:
            status['pending'] = False
        if 'running' not in status:
            status['running'] = False
        if 'finished' not in status:
            status['finished'] = False
        if 'succeeded' not in status:
            status['succeeded'] = False
        if 'failed' not in status:
            status['failed'] = False
        if 'error' not in status:
            status['error'] = None
        return status


class ResourceTests(ResourceTestsBase):
    """Tests for :class:`retdec.resource.Resource`."""

    def test_id_returns_passed_id(self):
        r = Resource('ID', self.conn_mock)
        self.assertEqual(r.id, 'ID')

    def test_is_pending_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'pending': True
        })
        r = Resource('ID', self.conn_mock)

        pending = r.is_pending()

        self.assertTrue(pending)
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_is_running_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'running': True
        })
        r = Resource('ID', self.conn_mock)

        running = r.is_running()

        self.assertTrue(running)
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_has_finished_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'succeeded': True
        })
        r = Resource('ID', self.conn_mock)

        finished = r.has_finished()

        self.assertTrue(finished)
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_has_succeeded_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'succeeded': True
        })
        r = Resource('ID', self.conn_mock)

        succeeded = r.has_succeeded()

        self.assertTrue(succeeded)
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_has_failed_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True
        })
        r = Resource('ID', self.conn_mock)

        failed = r.has_failed()

        self.assertTrue(failed)
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_get_error_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn_mock.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'Error message.'
        })
        r = Resource('ID', self.conn_mock)

        error = r.get_error()

        self.assertEqual(error, 'Error message.')
        self.conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_two_successive_state_queries_do_not_result_into_two_status_checks(self):
        # A certain time interval has to pass between checks successive checks
        # for the resource to query its status.
        self.conn_mock.send_get_request.side_effect = [
            self.status_with({
                'pending': True
            }), self.status_with({
                'pending': False
            })
        ]
        r = Resource('ID', self.conn_mock)

        r.is_pending()
        pending = r.is_pending()

        self.assertEqual(len(self.conn_mock.send_get_request.mock_calls), 1)
        self.assertTrue(pending)  # Still True because there was only one query.
