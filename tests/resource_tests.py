"""
    Tests for the :mod:`retdec.resource` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import unittest
from unittest import mock

from retdec.conn import APIConnection
from retdec.resource import Resource


class ResourceTests(unittest.TestCase):
    """Tests for :class:`retdec.resource.Resource`."""

    def test_id_returns_passed_id(self):
        r = Resource('ID', mock.Mock(spec_set=APIConnection))
        self.assertEqual(r.id, 'ID')

    def test_wait_until_finished_returns_when_resource_is_finished(self):
        conn_mock = mock.Mock(spec_set=APIConnection)
        conn_mock.send_get_request.return_value = {'finished': True}

        r = Resource('ID', conn_mock)

        r.wait_until_finished()

        conn_mock.send_get_request.assert_called_once_with('/ID/status')
