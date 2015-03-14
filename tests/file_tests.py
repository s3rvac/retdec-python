#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.file` module."""

import io
import unittest
from unittest import mock

from retdec.file import File


class AnyFile:
    """A matcher that matches any :class:`retdec.file.File`.
    """

    def __eq__(self, other):
        return isinstance(other, File)

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return '<{}>'.format(
            __name__ + '.' + self.__class__.__qualname__
        )


class AnyFileNamed:
    """A matcher that matches any :class:`retdec.file.File` that has the given
    name.
    """

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return (isinstance(other, File) and other.name == self.name)

    def __neq__(self, other):
        return not self == other

    def __repr__(self):
        return '<{} name={!r}>'.format(
            __name__ + '.' + self.__class__.__qualname__,
            self.name
        )


class FileTests(unittest.TestCase):
    """Tests for :class:`retdec.file.File`."""

    def test_file_is_used_directly_when_opened_file_is_given(self):
        file = mock.Mock()
        f = File(file)
        f.read()
        file.read.assert_called_once_with()

    @mock.patch('builtins.open')
    def test_file_is_opened_when_path_is_given(self, open):
        file = mock.Mock()
        open.return_value = file
        f = File('test.txt')
        f.read()
        open.assert_called_once_with('test.txt', 'rb')
        file.read.assert_called_once_with()

    def test_name_returns_custom_name_when_given(self):
        f = File(io.StringIO('...'), 'file.txt')
        self.assertEqual(f.name, 'file.txt')

    def test_name_returns_original_name_when_no_custom_name_is_given(self):
        file = mock.Mock()
        file.name = 'file.txt'
        f = File(file)
        self.assertEqual(f.name, 'file.txt')

    def test_name_returns_none_when_file_has_no_name(self):
        f = File(io.StringIO('...'))
        self.assertIsNone(f.name)

    def test_mode_returns_original_mode_when_underlying_file_has_mode(self):
        file = mock.Mock()
        file.mode = 'r+'
        f = File(file)
        self.assertEqual(f.mode, 'r+')

    def test_mode_returns_none_when_underlying_file_has_no_mode(self):
        f = File(io.StringIO('...'))
        self.assertIsNone(f.mode)

    def test_repr_returns_correct_value(self):
        f = File(io.StringIO('...'), name='file.txt')
        self.assertEqual(repr(f), "<retdec.file.File name='file.txt' mode=None>")
