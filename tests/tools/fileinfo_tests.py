#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.fileinfo` module."""

from retdec import DEFAULT_API_URL
from retdec import __version__
from retdec.fileinfo import Fileinfo
from retdec.tools.fileinfo import main
from retdec.tools.fileinfo import parse_args
from tests import mock
from tests.tools import ToolTestsBase


class ParseArgsTests(ToolTestsBase):
    """Tests for :func:`retdec.tools.fileinfo.parse_args()`."""

    def test_file_is_required(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['fileinfo.py'])
        self.assertNotEqual(cm.exception.code, 0)

    def test_file_is_parsed_correctly(self):
        args = parse_args(['fileinfo.py', 'prog.exe'])

        self.assertEqual(args.input_file, 'prog.exe')

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

    def test_output_format_is_parsed_correctly_short_form(self):
        args = parse_args(['fileinfo.py', '-f', 'json', 'prog.exe'])

        self.assertEqual(args.output_format, 'json')

    def test_output_format_is_parsed_correctly_long_form(self):
        args = parse_args(['fileinfo.py', '--output-format', 'json', 'prog.exe'])

        self.assertEqual(args.output_format, 'json')

    def test_verbose_is_parsed_correctly_short_form(self):
        args = parse_args(['fileinfo.py', '-v', 'prog.exe'])

        self.assertTrue(args.verbose)

    def test_verbose_is_parsed_correctly_long_form(self):
        args = parse_args(['fileinfo.py', '--verbose', 'prog.exe'])

        self.assertTrue(args.verbose)

    def test_prints_version_when_requested_and_exits(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['fileinfo.py', '--version'])
        self.assertEqual(cm.exception.code, 0)
        # Python < 3.4 emits the version to stderr, Python >= 3.4 to stdout.
        output = self.stdout.getvalue() + self.stderr.getvalue()
        self.assertIn(__version__, output)


class MainTests(ToolTestsBase):
    """Tests for :func:`retdec.tools.fileinfo.main()`."""

    def setUp(self):
        super().setUp()

        # Mock Fileinfo so that when it is instantiated, it returns our
        # fileinfo that can be used in the tests.
        self.fileinfo = mock.Mock(spec_set=Fileinfo)
        self.FileinfoMock = mock.Mock()
        self.FileinfoMock.return_value = self.fileinfo
        self.patch(
            'retdec.tools.fileinfo.Fileinfo',
            self.FileinfoMock
        )

    def test_performs_correct_actions(self):
        self.fileinfo.start_analysis.return_value.get_output.return_value = 'OUTPUT'

        main(['fileinfo.py', '--api-key', 'API-KEY', 'prog.exe'])

        # Fileinfo is instantiated with correct arguments.
        self.FileinfoMock.assert_called_once_with(
            api_url=DEFAULT_API_URL,
            api_key='API-KEY'
        )

        # Analysis is started with correct arguments.
        self.fileinfo.start_analysis.assert_called_once_with(
            input_file='prog.exe',
            output_format='plain',
            verbose=False
        )

        # The tool waits until the analysis is finished.
        analysis = self.fileinfo.start_analysis()
        analysis.wait_until_finished.assert_called_once_with()

        # The output from the analysis is written to the standard output.
        self.assertEqual(self.stdout.getvalue(), 'OUTPUT')
