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
