#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.resource` module."""

import datetime
import io
import os
import unittest

from retdec.conn import APIConnection
from retdec.resource import Resource
from tests import WithPatching
from tests import mock


class ResourceTestsBase(unittest.TestCase, WithPatching):
    """Base class for tests of :class:`retdec.resource.Resource` and its
    subclasses.
    """

    def setUp(self):
        super().setUp()

        self.conn = mock.Mock(spec_set=APIConnection)

        # Patch time.sleep() to prevent sleeping during tests.
        self.time_sleep = mock.Mock()
        self.patch('time.sleep', self.time_sleep)

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

    def assert_get_request_was_sent_with(self, path, params=None):
        """Asserts that a GET request was sent with the given path and
        parameters.
        """
        if params is not None:
            self.conn.send_get_request.assert_called_once_with(path, params)
        else:
            self.conn.send_get_request.assert_called_once_with(path)


# Do not inherit from unittest.TestCase because WithDisabledWaitingInterval is
# a mixin, not a base class for tests.
class WithDisabledWaitingInterval:
    """Mixin for tests that wish to disable the waiting interval.

    When the waiting interval is disabled, the status is checked in every
    state-querying method call. As a result, there is no busy-waiting.

    When using the mixin, always put it before classes that inherit from
    ``unittest.TestCase``. Otherwise, their setUp() method is not called
    because ``unittest.TestCase.setUp()`` does not call ``super().setUp()``.
    See http://nedbatchelder.com/blog/201210/multiple_inheritance_is_hard.html
    for more details.
    """

    def setUp(self):
        super().setUp()

        # Disable the waiting interval so that the status is checked in every
        # state-querying method call.
        self._orig_state_update_interval = Resource._STATE_UPDATE_INTERVAL
        Resource._STATE_UPDATE_INTERVAL = datetime.timedelta(seconds=0)

    def tearDown(self):
        super().tearDown()

        # Restore the waiting interval.
        Resource._STATE_UPDATE_INTERVAL = self._orig_state_update_interval


# Do not inherit from unittest.TestCase because WithMockedIO is
# a mixin, not a base class for tests.
class WithMockedIO(WithPatching):
    """Mixin for tests that call functions that perform I/O operations.

    When using the mixin, always put it before classes that inherit from
    ``unittest.TestCase``. Otherwise, their setUp() method is not called
    because ``unittest.TestCase.setUp()`` does not call ``super().setUp()``.
    See http://nedbatchelder.com/blog/201210/multiple_inheritance_is_hard.html
    for more details.
    """

    def setUp(self):
        super().setUp()

        self.open = mock.mock_open()
        self.patch('builtins.open', self.open)

        self.shutil = mock.Mock()
        self.patch('retdec.resource.shutil', self.shutil)

    def assert_obtains_file_contents(self, func, file_path, is_text_file):
        """Asserts that ``func()`` obtains the contents of the given file.

        :param callable func: Function to be called.
        :param str file_path: Path to the file to be downloaded.
        :param bool is_text_file: Is it a text file or a binary file?
        """
        self.conn.get_file.return_value = io.BytesIO(b'data')

        output = func()

        self.assertEqual(output, 'data' if is_text_file else b'data')
        self.conn.get_file.assert_called_once_with(file_path)

    def assert_obtains_and_saves_file(self, func, file_path, directory):
        """Asserts that ``func(directory)`` obtains the given file and saves it
        to `directory`.

        :param callable func: Function to be called with `directory`.
        :param str file_path: Path to the file to be downloaded.
        :param str directory: Directory in which the file will be stored.

        If `directory` is ``None``, the current working directory is used.
        """
        file = mock.Mock()
        file.name = 'file_name'
        self.conn.get_file.return_value = file

        saved_file_path = func(directory)

        self.conn.get_file.assert_called_once_with(file_path)
        directory = directory or os.getcwd()
        ref_saved_file_path = os.path.join(directory, 'file_name')
        self.open.assert_called_once_with(
            ref_saved_file_path,
            'wb'
        )
        self.assertEqual(ref_saved_file_path, saved_file_path)


class ResourceTests(ResourceTestsBase):
    """Tests for :class:`retdec.resource.Resource`."""

    def test_id_returns_passed_id(self):
        r = Resource('ID', self.conn)
        self.assertEqual(r.id, 'ID')

    def test_is_pending_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'pending': True
        })
        r = Resource('ID', self.conn)

        pending = r.is_pending()

        self.assertTrue(pending)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_is_running_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'running': True
        })
        r = Resource('ID', self.conn)

        running = r.is_running()

        self.assertTrue(running)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_has_finished_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'succeeded': True
        })
        r = Resource('ID', self.conn)

        finished = r.has_finished()

        self.assertTrue(finished)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_has_succeeded_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'succeeded': True
        })
        r = Resource('ID', self.conn)

        succeeded = r.has_succeeded()

        self.assertTrue(succeeded)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_has_failed_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True
        })
        r = Resource('ID', self.conn)

        failed = r.has_failed()

        self.assertTrue(failed)
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_get_error_checks_status_on_first_call_and_returns_correct_value(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'Error message.'
        })
        r = Resource('ID', self.conn)

        error = r.get_error()

        self.assertEqual(error, 'Error message.')
        self.conn.send_get_request.assert_called_once_with('/ID/status')

    def test_two_successive_state_queries_do_not_result_into_two_status_checks(self):
        # A certain time interval has to pass between successive checks for the
        # resource to query its status.
        self.conn.send_get_request.side_effect = [
            self.status_with({
                'pending': True
            }), self.status_with({
                'pending': False
            })
        ]
        r = Resource('ID', self.conn)

        r.is_pending()
        pending = r.is_pending()

        self.assertEqual(len(self.conn.send_get_request.mock_calls), 1)
        self.assertTrue(pending)  # Still True because there was only one query.
