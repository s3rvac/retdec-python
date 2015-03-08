#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.decompiler` module."""

import os
import unittest

from retdec.tools.decompiler import get_output_dir
from retdec.tools.decompiler import parse_args
from tests.tools import ParseArgsBaseTests


class ParseArgsTests(ParseArgsBaseTests):
    """Tests for :func:`retdec.tools.decompiler.parse_args()`."""

    def test_file_is_required(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['decompiler.py'])
        self.assertNotEqual(cm.exception.code, 0)

    def test_file_is_parsed_correctly(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertEqual(args.file, 'prog.exe')

    def test_api_key_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-k', 'KEY', 'prog.exe'])
        self.assertEqual(args.api_key, 'KEY')

    def test_api_key_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--api-key', 'KEY', 'prog.exe'])
        self.assertEqual(args.api_key, 'KEY')

    def test_api_url_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-u', 'URL', 'prog.exe'])
        self.assertEqual(args.api_url, 'URL')

    def test_api_url_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--api-url', 'URL', 'prog.exe'])
        self.assertEqual(args.api_url, 'URL')

    def test_mode_is_set_to_none_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertIsNone(args.mode)

    def test_mode_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-m', 'bin', 'prog.exe'])
        self.assertEqual(args.mode, 'bin')

    def test_mode_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--mode', 'bin', 'prog.exe'])
        self.assertEqual(args.mode, 'bin')

    def test_output_dir_is_set_to_none_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertIsNone(args.output_dir)

    def test_output_dir_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-o', 'dir', 'prog.exe'])
        self.assertEqual(args.output_dir, 'dir')

    def test_output_dir_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--output-dir', 'dir', 'prog.exe'])
        self.assertEqual(args.output_dir, 'dir')


class GetOutputDirTests(unittest.TestCase):
    """Tests for :func:`retdec.tools.decompiler.get_output_dir()`."""

    def test_returns_correct_dir_when_output_dir_is_not_given(self):
        input_file = os.path.join('dir', 'prog.exe')

        output_dir = get_output_dir(input_file, output_dir=None)

        self.assertEqual(
            output_dir,
            os.path.join(os.getcwd(), 'dir')
        )
        self.assertTrue(os.path.isabs(output_dir))

    def test_returns_correct_dir_when_output_dir_is_given(self):
        input_file = os.path.join('dir', 'prog.exe')

        output_dir = get_output_dir(input_file, output_dir='other_dir')

        self.assertEqual(
            output_dir,
            os.path.join(os.getcwd(), 'other_dir')
        )
        self.assertTrue(os.path.isabs(output_dir))
