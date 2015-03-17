#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.decompiler` module."""

import io
import os
import unittest
from unittest import mock

from retdec import DEFAULT_API_URL
from retdec.decompiler import Decompilation
from retdec.decompiler import DecompilationPhase
from retdec.decompiler import Decompiler
from retdec.tools.decompiler import NoProgressDisplayer
from retdec.tools.decompiler import ProgressBarDisplayer
from retdec.tools.decompiler import ProgressLogDisplayer
from retdec.tools.decompiler import display_download_progress
from retdec.tools.decompiler import get_output_dir
from retdec.tools.decompiler import get_progress_displayer
from retdec.tools.decompiler import main
from retdec.tools.decompiler import parse_args
from tests.tools import ToolTestsBase


class ProgressDisplayerTestsBase(unittest.TestCase):
    """Base class of progress displayers."""

    def setUp(self):
        super().setUp()

        # Patch sys.stdout (the displayers print the progress in it).
        self.stdout = io.StringIO()
        patcher = mock.patch('sys.stdout', self.stdout)
        patcher.start()
        self.addCleanup(patcher.stop)


class ProgressBarDisplayerTests(ProgressDisplayerTestsBase):
    """Tests for :class:`retdec.tools.decompiler.ProgressBarDisplayer`."""

    def test_display_decompilation_progress_successful_decompilation(self):
        displayer = ProgressBarDisplayer()
        decompilation = mock.Mock(spec_set=Decompilation)
        decompilation.id = '8DRerEdKop'
        decompilation.get_completion.return_value = 100
        decompilation.has_finished.return_value = True
        decompilation.has_succeeded.return_value = True

        displayer.display_decompilation_progress(decompilation)

        self.assertEqual(
            self.stdout.getvalue(),
            '\r8DRerEdKop: [########################################] 100% OK\n'
        )

    def test_display_decompilation_progress_failed_decompilation(self):
        displayer = ProgressBarDisplayer()
        decompilation = mock.Mock(spec_set=Decompilation)
        decompilation.id = '8DRerEdKop'
        decompilation.get_completion.return_value = 100
        decompilation.has_finished.return_value = True
        decompilation.has_succeeded.return_value = False

        displayer.display_decompilation_progress(decompilation)

        self.assertEqual(
            self.stdout.getvalue(),
            '\r8DRerEdKop: [########################################] 100% FAIL\n'
        )

    def test_display_download_progress_does_nothing(self):
        displayer = ProgressBarDisplayer()

        displayer.display_download_progress('test.out.c')

        self.assertEqual(self.stdout.getvalue(), '')

    def test_repr_returns_correct_value(self):
        displayer = ProgressBarDisplayer()
        self.assertEqual(
            repr(displayer),
            '<retdec.tools.decompiler.ProgressBarDisplayer>'
        )


class ProgressLogDisplayerTests(ProgressDisplayerTestsBase):
    """Tests for :class:`retdec.tools.decompiler.ProgressLogDisplayer`."""

    def test_display_decompilation_progress_displays_correct_value_successful_decompilation(self):
        displayer = ProgressLogDisplayer()
        d = mock.MagicMock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = False
        d.get_phases.return_value = [
            DecompilationPhase(
                name='Waiting For Resources',
                part=None,
                description='Waiting for resources',
                completion=0
            ),
            DecompilationPhase(
                name='File Information',
                part='Pre-Processing',
                description='Obtaining file information',
                completion=5
            ),
            DecompilationPhase(
                name='Done',
                part=None,
                description='Done',
                completion=100
            )
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Waiting for resources (0%)...                      [OK]
Pre-Processing:
    Obtaining file information (5%)...             [OK]
Done (100%)...                                     \n""".lstrip())

    def test_display_decompilation_progress_displays_correct_value_failed_decompilation(self):
        displayer = ProgressLogDisplayer()
        d = mock.MagicMock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = True
        d.get_phases.return_value = [
            DecompilationPhase(
                name='Waiting For Resources',
                part=None,
                description='Waiting for resources',
                completion=0
            )
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Waiting for resources (0%)...                      [FAIL]
""".lstrip())

    def test_display_download_progress_displays_correct_value(self):
        displayer = ProgressLogDisplayer()

        displayer.display_download_progress('test.out.c')

        self.assertEqual(
            self.stdout.getvalue(),
            ('\nDownloading:\n'
             ' - test.out.c\n')
        )

    def test_repr_returns_correct_value(self):
        displayer = ProgressLogDisplayer()
        self.assertEqual(
            repr(displayer),
            '<retdec.tools.decompiler.ProgressLogDisplayer>'
        )


class NoProgressDisplayerTests(ProgressDisplayerTestsBase):
    """Tests for :class:`retdec.tools.decompiler.NoProgressDisplayer`."""

    def test_display_decompilation_progress_does_nothing(self):
        displayer = NoProgressDisplayer()

        displayer.display_decompilation_progress(mock.Mock())

        self.assertEqual(self.stdout.getvalue(), '')

    def test_display_download_progress_does_nothing(self):
        displayer = NoProgressDisplayer()

        displayer.display_download_progress('test.out.c')

        self.assertEqual(self.stdout.getvalue(), '')

    def test_repr_returns_correct_value(self):
        displayer = NoProgressDisplayer()
        self.assertEqual(
            repr(displayer),
            '<retdec.tools.decompiler.NoProgressDisplayer>'
        )


class ParseArgsTests(ToolTestsBase):
    """Tests for :func:`retdec.tools.decompiler.parse_args()`."""

    def test_file_is_required(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['decompiler.py'])
        self.assertNotEqual(cm.exception.code, 0)

    def test_file_is_parsed_correctly(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertEqual(args.input_file, 'prog.exe')

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

    def test_quiet_is_set_to_false_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertFalse(args.quiet)

    def test_quiet_is_set_to_true_when_given_in_short_form(self):
        args = parse_args(['decompiler.py', '-q', 'prog.exe'])
        self.assertTrue(args.quiet)

    def test_quiet_is_set_to_true_when_given_in_long_form(self):
        args = parse_args(['decompiler.py', '--quiet', 'prog.exe'])
        self.assertTrue(args.quiet)

    def test_brief_is_set_to_false_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])
        self.assertFalse(args.brief)

    def test_brief_is_set_to_true_when_given_in_short_form(self):
        args = parse_args(['decompiler.py', '-b', 'prog.exe'])
        self.assertTrue(args.brief)

    def test_brief_is_set_to_true_when_given_in_long_form(self):
        args = parse_args(['decompiler.py', '--brief', 'prog.exe'])
        self.assertTrue(args.brief)


class FakeArguments:
    """Fake representation of tool arguments."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class GetOutputDirTests(unittest.TestCase):
    """Tests for :func:`retdec.tools.decompiler.get_output_dir()`."""

    def test_returns_correct_dir_when_output_dir_is_not_given(self):
        input_file = os.path.join('dir', 'prog.exe')
        args = FakeArguments(input_file=input_file, output_dir=None)

        output_dir = get_output_dir(args)

        self.assertEqual(
            output_dir,
            os.path.join(os.getcwd(), 'dir')
        )
        self.assertTrue(os.path.isabs(output_dir))

    def test_returns_correct_dir_when_output_dir_is_given(self):
        input_file = os.path.join('dir', 'prog.exe')
        args = FakeArguments(input_file=input_file, output_dir='other_dir')

        output_dir = get_output_dir(args)

        self.assertEqual(
            output_dir,
            os.path.join(os.getcwd(), 'other_dir')
        )
        self.assertTrue(os.path.isabs(output_dir))


class GetProgressCallbackTests(unittest.TestCase):
    """Tests for :func:`retdec.tools.decompiler.get_progress_displayer()`."""

    def test_returns_progress_log_displayer_by_default(self):
        args = FakeArguments(quiet=False, brief=False)

        displayer = get_progress_displayer(args)

        self.assertIsInstance(displayer, ProgressLogDisplayer)

    def test_returns_progress_bar_displayer_if_brief_is_set(self):
        args = FakeArguments(quiet=False, brief=True)

        displayer = get_progress_displayer(args)

        self.assertIsInstance(displayer, ProgressBarDisplayer)

    def test_returns_no_progress_displayer_if_quiet_is_set(self):
        args = FakeArguments(quiet=True, brief=False)

        displayer = get_progress_displayer(args)

        self.assertIsInstance(displayer, NoProgressDisplayer)


class DisplayDownloadProgressTests(unittest.TestCase):
    """Tests for :func:`retdec.tools.decompiler.display_download_progress()`.
    """

    def test_calls_display_on_displayer_with_file_name(self):
        displayer = mock.Mock(spec_set=ProgressLogDisplayer)

        display_download_progress(displayer, 'dir/file_name')

        displayer.display_download_progress.assert_called_once_with('file_name')


class MainTests(ToolTestsBase):
    """Tests for :func:`retdec.tools.decompiler.main()`."""

    def setUp(self):
        super().setUp()

        # Mock Decompiler so that when it is instantiated, it returns our
        # decompiler that can be used in the tests.
        self.decompiler = mock.MagicMock(spec_set=Decompiler)
        self.DecompilerMock = mock.Mock()
        self.DecompilerMock.return_value = self.decompiler
        patcher = mock.patch(
            'retdec.tools.decompiler.Decompiler',
            self.DecompilerMock
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_performs_correct_actions_when_only_api_key_and_input_file_are_given(self):
        self.decompiler.run_decompilation.return_value.get_output.return_value = 'OUTPUT'

        main(['decompiler.py', '--api-key', 'API-KEY', 'prog.exe'])

        # Decompiler is instantiated with correct arguments.
        self.DecompilerMock.assert_called_once_with(
            api_url=DEFAULT_API_URL,
            api_key='API-KEY'
        )

        # Decompilation is run with correct arguments.
        self.decompiler.run_decompilation.assert_called_once_with(
            input_file='prog.exe',
            mode=None
        )

        # The tool waits until the decompilation is finished.
        decompilation = self.decompiler.run_decompilation()
        self.assertEqual(
            len(decompilation.wait_until_finished.mock_calls), 1
        )

        # The generated HLL is saved.
        decompilation.save_output_hll.assert_called_once_with(os.getcwd())

        # The generated DSM is saved.
        decompilation.save_output_dsm.assert_called_once_with(os.getcwd())
