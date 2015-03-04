#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.resource` module."""

import unittest
from unittest import mock

from retdec.conn import APIConnection
from retdec.exceptions import ResourceFailedError
from retdec.resource import Resource


class ResourceTests(unittest.TestCase):
    """Tests for :class:`retdec.resource.Resource`."""

    def test_id_returns_passed_id(self):
        r = Resource('ID', mock.Mock(spec_set=APIConnection))
        self.assertEqual(r.id, 'ID')


class ResourceWaitUntilFinishedTests(unittest.TestCase):
    """Tests for :func:`retdec.resource.Resource.wait_until_finished()`."""

    def test_returns_when_resource_is_finished(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {
            'completion': 100,
            'finished': True,
            'failed': False
        }
        r = Resource('ID', conn_mock)

        r.wait_until_finished()

        conn_mock.send_get_request.assert_called_once_with('/ID/status')

    def test_calls_callback_when_resource_finishes(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {
            'completion': 100,
            'finished': True,
            'failed': False
        }
        r = Resource('ID', conn_mock)
        callback = mock.Mock()

        r.wait_until_finished(callback)

        callback.assert_called_once_with(r)

    @mock.patch('time.sleep')
    def test_calls_callback_when_resource_status_changes(self, sleep_mock):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.side_effect = [
            {'completion': 0, 'finished': False},
            {'completion': 15, 'finished': False},
            {'completion': 100, 'finished': True, 'failed': False}
        ]
        r = Resource('ID', conn_mock)
        callback = mock.Mock()

        r.wait_until_finished(callback)

        self.assertEqual(len(callback.mock_calls), 2)

    def test_raises_exception_by_default_when_resource_failed(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {
            'completion': 45,
            'finished': True,
            'failed': True,
            'error': 'error message'
        }
        r = Resource('ID', conn_mock)

        with self.assertRaises(ResourceFailedError):
            r.wait_until_finished()

    def test_calls_on_failure_when_it_is_callable(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {
            'completion': 45,
            'finished': True,
            'failed': True,
            'error': 'error message'
        }
        r = Resource('ID', conn_mock)
        on_failure_mock = mock.Mock()

        r.wait_until_finished(on_failure=on_failure_mock)

        on_failure_mock.assert_called_once_with('error message')

    def test_does_not_raise_exception_when_on_failure_is_none(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {
            'completion': 45,
            'finished': True,
            'failed': True,
            'error': 'error message'
        }
        r = Resource('ID', conn_mock)

        r.wait_until_finished(on_failure=None)
