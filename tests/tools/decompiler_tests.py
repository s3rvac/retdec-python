#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.decompiler` module."""

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
