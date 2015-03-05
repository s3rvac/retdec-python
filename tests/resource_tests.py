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
        # Patch time.sleep() to prevent sleeping during tests.
        self.time_sleep_mock = mock.Mock()
        patcher = mock.patch('time.sleep', self.time_sleep_mock)
        patcher.start()
        self.addCleanup(patcher.stop)


class ResourceTests(ResourceTestsBase):
    """Tests for :class:`retdec.resource.Resource`."""

    def test_id_returns_passed_id(self):
        r = Resource('ID', mock.Mock(spec_set=APIConnection))
        self.assertEqual(r.id, 'ID')
