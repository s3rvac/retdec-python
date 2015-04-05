#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.fileinfo` module."""

from unittest import mock

from retdec import DEFAULT_API_URL
from retdec.fileinfo import Fileinfo
from retdec.tools.fileinfo import main
from retdec.tools.fileinfo import parse_args
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

    def test_verbose_is_parsed_correctly_short_form(self):
        args = parse_args(['fileinfo.py', '-v', 'prog.exe'])
        self.assertTrue(args.verbose)

    def test_verbose_is_parsed_correctly_long_form(self):
        args = parse_args(['fileinfo.py', '--verbose', 'prog.exe'])
        self.assertTrue(args.verbose)


class MainTests(ToolTestsBase):
    """Tests for :func:`retdec.tools.fileinfo.main()`."""

    def setUp(self):
        super().setUp()

        # Mock Fileinfo so that when it is instantiated, it returns our
        # fileinfo that can be used in the tests.
        self.fileinfo = mock.MagicMock(spec_set=Fileinfo)
        self.FileinfoMock = mock.Mock()
        self.FileinfoMock.return_value = self.fileinfo
        self.patch(
            'retdec.tools.fileinfo.Fileinfo',
            self.FileinfoMock
        )

    def test_performs_correct_actions(self):
        self.fileinfo.run_analysis.return_value.get_output.return_value = 'OUTPUT'

        main(['fileinfo.py', '--api-key', 'API-KEY', 'prog.exe'])

        # Fileinfo is instantiated with correct arguments.
        self.FileinfoMock.assert_called_once_with(
            api_url=DEFAULT_API_URL,
            api_key='API-KEY'
        )

        # Analysis is run with correct arguments.
        self.fileinfo.run_analysis.assert_called_once_with(
            input_file='prog.exe',
            verbose=False
        )

        # The tool waits until the analysis is finished.
        analysis = self.fileinfo.run_analysis()
        analysis.wait_until_finished.assert_called_once_with()

        # The output from the analysis is written to the standard output.
        self.assertEqual(self.stdout.getvalue(), 'OUTPUT')
