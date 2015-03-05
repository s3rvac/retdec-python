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
