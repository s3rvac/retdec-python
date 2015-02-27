"""
    Tests for the :mod:`retdec.tools.fileinfo` module.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

from retdec.tools.fileinfo import parse_args
from tests.tools import ParseArgsBaseTests


class ParseArgsTests(ParseArgsBaseTests):
    """Tests for :func:`retdec.tools.fileinfo.parse_args()`."""

    def test_file_is_required(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['fileinfo.py'])
        self.assertNotEqual(cm.exception.code, 0)

    def test_file_is_parsed_correctly(self):
        args = parse_args(['fileinfo.py', 'prog.exe'])
        self.assertEqual(args.file, 'prog.exe')

    def test_api_key_is_parsed_correctly_short_form(self):
        args = parse_args(['fileinfo.py', '-k', 'KEY', 'prog.exe'])
        self.assertEqual(args.api_key, 'KEY')

    def test_api_key_is_parsed_correctly_long_form(self):
        args = parse_args(['fileinfo.py', '--api-key', 'KEY', 'prog.exe'])
        self.assertEqual(args.api_key, 'KEY')

    def test_api_url_is_parsed_correctly_short_form(self):
        args = parse_args(['fileinfo.py', '-u', 'URL', 'prog.exe'])
        self.assertEqual(args.api_url, 'URL')

    def test_api_url_is_parsed_correctly_long_form(self):
        args = parse_args(['fileinfo.py', '--api-url', 'URL', 'prog.exe'])
        self.assertEqual(args.api_url, 'URL')
