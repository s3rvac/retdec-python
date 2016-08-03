#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.tools.decompiler` module."""

import os
import unittest

from retdec import DEFAULT_API_URL
from retdec import __version__
from retdec.decompilation import Decompilation
from retdec.decompilation import DecompilationPhase
from retdec.decompiler import Decompiler
from retdec.tools.decompiler import NoProgressDisplayer
from retdec.tools.decompiler import ProgressBarDisplayer
from retdec.tools.decompiler import ProgressLogDisplayer
from retdec.tools.decompiler import display_download_progress
from retdec.tools.decompiler import get_output_dir
from retdec.tools.decompiler import get_progress_displayer
from retdec.tools.decompiler import main
from retdec.tools.decompiler import parse_args
from tests import mock
from tests.tools import ToolTestsBase


class ProgressBarDisplayerTests(ToolTestsBase):
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


class ProgressLogDisplayerTests(ToolTestsBase):
    """Tests for :class:`retdec.tools.decompiler.ProgressLogDisplayer`."""

    def test_display_decompilation_progress_displays_correct_value_successful_decompilation(self):
        displayer = ProgressLogDisplayer()
        d = mock.Mock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = False
        d.get_phases.return_value = [
            DecompilationPhase(
                name='Waiting For Resources',
                part=None,
                description='Waiting for resources',
                completion=0,
                warnings=[]
            ),
            DecompilationPhase(
                name='File Information',
                part='Pre-Processing',
                description='Obtaining file information',
                completion=5,
                warnings=[]
            ),
            DecompilationPhase(
                name='Done',
                part=None,
                description='Done',
                completion=100,
                warnings=[]
            )
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Waiting for resources (0%)...                      [OK]
Pre-Processing:
  Obtaining file information (5%)...               [OK]
Done (100%)...                                     \n""".lstrip())

    def test_display_decompilation_progress_displays_correct_value_failed_decompilation(self):
        displayer = ProgressLogDisplayer()
        d = mock.Mock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = True
        d.get_phases.return_value = [
            DecompilationPhase(
                name='Waiting For Resources',
                part=None,
                description='Waiting for resources',
                completion=0,
                warnings=[]
            )
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Waiting for resources (0%)...                      [FAIL]
""".lstrip())

    def test_display_decompilation_progress_shows_warnings_in_intermediate_phase(self):
        displayer = ProgressLogDisplayer()
        d = mock.Mock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = False
        d.get_phases.return_value = [
            DecompilationPhase(
                name='File Information',
                part='Pre-Processing',
                description='Obtaining file information',
                completion=5,
                warnings=[
                    'warning1',
                    'warning2'
                ]
            ),
            DecompilationPhase(
                name='Done',
                part=None,
                description='Done',
                completion=100,
                warnings=[]
            )
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Pre-Processing:
  Obtaining file information (5%)...               [OK]
Warning: warning1
Warning: warning2
Done (100%)...                                     \n""".lstrip())

    def test_display_decompilation_progress_shows_warnings_in_last_phase(self):
        displayer = ProgressLogDisplayer()
        d = mock.Mock(spec_set=Decompilation)
        d.id = 'ID'
        d.has_finished.return_value = True
        d.has_failed.return_value = True
        d.get_phases.return_value = [
            DecompilationPhase(
                name='File Information',
                part='Pre-Processing',
                description='Obtaining file information',
                completion=5,
                warnings=[
                    'warning1',
                    'warning2'
                ]
            ),
        ]

        displayer.display_decompilation_progress(d)

        self.assertEqual(
            self.stdout.getvalue(), """
ID
--

Pre-Processing:
  Obtaining file information (5%)...               [FAIL]
Warning: warning1
Warning: warning2
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


class NoProgressDisplayerTests(ToolTestsBase):
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

    def test_pdb_file_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-p', 'prog.pdb', 'prog.exe'])

        self.assertEqual(args.pdb_file, 'prog.pdb')

    def test_pdb_file_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--pdb-file', 'prog.pdb', 'prog.exe'])

        self.assertEqual(args.pdb_file, 'prog.pdb')

    def test_quiet_is_set_to_false_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])

        self.assertFalse(args.quiet)

    def test_quiet_is_set_to_true_when_given_in_short_form(self):
        args = parse_args(['decompiler.py', '-q', 'prog.exe'])

        self.assertTrue(args.quiet)

    def test_quiet_is_set_to_true_when_given_in_long_form(self):
        args = parse_args(['decompiler.py', '--quiet', 'prog.exe'])

        self.assertTrue(args.quiet)

    def test_target_language_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-l', 'py', 'prog.exe'])

        self.assertEqual(args.target_language, 'py')

    def test_target_language_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--target-language', 'py', 'prog.exe'])

        self.assertEqual(args.target_language, 'py')

    def test_graph_format_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--graph-forma', 'svg', 'prog.exe'])

        self.assertEqual(args.graph_format, 'svg')

    def test_architecture_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-a', 'arm', 'file.c'])

        self.assertEqual(args.architecture, 'arm')

    def test_architecture_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--architecture', 'arm', 'file.c'])

        self.assertEqual(args.architecture, 'arm')

    def test_file_format_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-f', 'elf', 'file.c'])

        self.assertEqual(args.file_format, 'elf')

    def test_file_format_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--file-format', 'elf', 'file.c'])

        self.assertEqual(args.file_format, 'elf')

    def test_comp_compiler_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-c', 'clang', 'file.c'])

        self.assertEqual(args.comp_compiler, 'clang')

    def test_comp_compiler_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--compiler', 'clang', 'file.c'])

        self.assertEqual(args.comp_compiler, 'clang')

    def test_comp_optimizations_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-C', 'O1', 'file.c'])

        self.assertEqual(args.comp_optimizations, 'O1')

    def test_comp_optimizations_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--compiler-optimizations', 'O1', 'file.c'])

        self.assertEqual(args.comp_optimizations, 'O1')

    def test_comp_debug_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-g', 'file.c'])

        self.assertTrue(args.comp_debug)

    def test_comp_debug_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--compiler-debug', 'file.c'])

        self.assertTrue(args.comp_debug)

    def test_comp_strip_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-s', 'file.c'])

        self.assertTrue(args.comp_strip)

    def test_comp_strip_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--compiler-strip', 'file.c'])

        self.assertTrue(args.comp_strip)

    def test_decomp_var_names_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--var-names', 'simple', 'prog.exe'])

        self.assertEqual(args.decomp_var_names, 'simple')

    def test_decomp_optimizations_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-O', 'none', 'prog.exe'])

        self.assertEqual(args.decomp_optimizations, 'none')

    def test_decomp_optimizations_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--optimizations', 'none', 'prog.exe'])

        self.assertEqual(args.decomp_optimizations, 'none')

    def test_decomp_unreach_funcs_is_parsed_correctly_short_form(self):
        args = parse_args(['decompiler.py', '-K', 'prog.exe'])

        self.assertTrue(args.decomp_unreach_funcs)

    def test_decomp_unreach_funcs_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--keep-unreach-funcs', 'prog.exe'])

        self.assertTrue(args.decomp_unreach_funcs)

    def test_decomp_emit_addresses_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--no-addresses', 'prog.exe'])

        self.assertFalse(args.decomp_emit_addresses)

    def test_decomp_sel_funcs_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--only-funcs', 'func1,func2', 'prog.exe'])

        self.assertEqual(args.sel_decomp_funcs, 'func1,func2')

    def test_decomp_sel_ranges_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--only-ranges', '0x0-0x2,0x7-0x9', 'prog.exe'])

        self.assertEqual(args.sel_decomp_ranges, '0x0-0x2,0x7-0x9')

    def test_decomp_sel_decoding_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--decoding', 'only', 'prog.exe'])

        self.assertEqual(args.sel_decomp_decoding, 'only')

    def test_decomp_raw_endian_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--raw-endian', 'big', 'prog.exe'])

        self.assertEqual(args.raw_endian, 'big')

    def test_decomp_raw_entry_point_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--raw-entry-point', '0x8000', 'prog.exe'])

        self.assertEqual(args.raw_entry_point, '0x8000')

    def test_decomp_raw_section_vma_is_parsed_correctly_long_form(self):
        args = parse_args(['decompiler.py', '--raw-section-vma', '0x8000', 'prog.exe'])

        self.assertEqual(args.raw_section_vma, '0x8000')

    def test_generate_archive_is_set_to_true_when_with_archive_given(self):
        args = parse_args(['decompiler.py', '--with-archive', 'prog.exe'])

        self.assertTrue(args.generate_archive)

    def test_generate_cg_is_set_to_true_when_with_cg_given(self):
        args = parse_args(['decompiler.py', '--with-cg', 'prog.exe'])

        self.assertTrue(args.generate_cg)

    def test_generate_cfgs_is_set_to_true_when_with_cfgs_given(self):
        args = parse_args(['decompiler.py', '--with-cfgs', 'prog.exe'])

        self.assertTrue(args.generate_cfgs)

    def test_brief_is_set_to_false_when_not_given(self):
        args = parse_args(['decompiler.py', 'prog.exe'])

        self.assertFalse(args.brief)

    def test_brief_is_set_to_true_when_given_in_short_form(self):
        args = parse_args(['decompiler.py', '-b', 'prog.exe'])

        self.assertTrue(args.brief)

    def test_brief_is_set_to_true_when_given_in_long_form(self):
        args = parse_args(['decompiler.py', '--brief', 'prog.exe'])

        self.assertTrue(args.brief)

    def test_prints_version_when_requested_and_exits(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['decompiler.py', '--version'])
        self.assertEqual(cm.exception.code, 0)
        # Python < 3.4 emits the version to stderr, Python >= 3.4 to stdout.
        output = self.stdout.getvalue() + self.stderr.getvalue()
        self.assertIn(__version__, output)


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
        self.patch(
            'retdec.tools.decompiler.Decompiler',
            self.DecompilerMock
        )

    def get_started_decompilation(self):
        """Returns a decompilation that has started.

        This method assumes that a decompilation has started.
        """
        return self.decompiler.start_decompilation()

    def test_performs_correct_actions_when_only_api_key_and_input_file_are_given(self):
        main(['decompiler.py', '--api-key', 'API-KEY', 'prog.exe'])

        # Decompiler is instantiated with correct arguments.
        self.DecompilerMock.assert_called_once_with(
            api_url=DEFAULT_API_URL,
            api_key='API-KEY'
        )

        # Decompilation is started with correct arguments.
        self.decompiler.start_decompilation.assert_called_once_with(
            input_file='prog.exe'
        )

        # The tool waits until the decompilation is finished.
        decompilation = self.get_started_decompilation()
        self.assertEqual(
            len(decompilation.wait_until_finished.mock_calls), 1
        )

        # The generated HLL code is saved.
        decompilation.save_hll_code.assert_called_once_with(os.getcwd())

        # The generated DSM code is saved.
        decompilation.save_dsm_code.assert_called_once_with(os.getcwd())

    def call_main_with_standard_arguments_and(self, *additional_args):
        """Calls ``main()`` with standard arguments (such as ``--api-key``),
        but also includes `additional_args`.
        """
        standard_args = (
            'decompiler.py',
            '--api-key', 'API-KEY',
            'prog.exe'
        )
        return main(standard_args + additional_args)

    def assert_decompilation_was_started_also_with(self, *args, **kwargs):
        """Asserts that the decompilation was also started with the given
        arguments.
        """
        decompilation_args = self.decompiler.start_decompilation.call_args
        for arg in args:
            self.assertIn(arg, decompilation_args[0])
        for key, value in kwargs.items():
            self.assertIn(key, decompilation_args[1])
            msg = "key is '{}'".format(key)
            self.assertEqual(decompilation_args[1][key], value, msg)

    def test_sets_target_language_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--target-language', 'py'
        )

        self.assert_decompilation_was_started_also_with(
            target_language='py'
        )

    def test_sets_graph_format_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--graph-format', 'svg'
        )

        self.assert_decompilation_was_started_also_with(
            graph_format='svg'
        )

    def test_sets_architecture_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--architecture', 'arm'
        )

        self.assert_decompilation_was_started_also_with(
            architecture='arm'
        )

    def test_sets_file_format_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--file-format', 'elf'
        )

        self.assert_decompilation_was_started_also_with(
            file_format='elf'
        )

    def test_sets_comp_compiler_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--compiler', 'clang'
        )

        self.assert_decompilation_was_started_also_with(
            comp_compiler='clang'
        )

    def test_sets_comp_optimizations_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--compiler-optimizations', 'O1'
        )

        self.assert_decompilation_was_started_also_with(
            comp_optimizations='O1'
        )

    def test_sets_comp_debug_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--compiler-debug'
        )

        self.assert_decompilation_was_started_also_with(
            comp_debug=True
        )

    def test_sets_comp_strip_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--compiler-strip'
        )

        self.assert_decompilation_was_started_also_with(
            comp_strip=True
        )

    def test_sets_decomp_var_names_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--var-names', 'simple'
        )

        self.assert_decompilation_was_started_also_with(
            decomp_var_names='simple'
        )

    def test_sets_decomp_optimizations_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--optimizations', 'none'
        )

        self.assert_decompilation_was_started_also_with(
            decomp_optimizations='none'
        )

    def test_sets_decomp_unreach_funcs_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--keep-unreach-funcs'
        )

        self.assert_decompilation_was_started_also_with(
            decomp_unreach_funcs=True
        )

    def test_sets_decomp_emit_addresses_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--no-addresses'
        )

        self.assert_decompilation_was_started_also_with(
            decomp_emit_addresses=False
        )

    def test_sets_sel_decomp_funcs_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--only-funcs', 'func1,func2'
        )

        self.assert_decompilation_was_started_also_with(
            sel_decomp_funcs='func1,func2'
        )

    def test_sets_sel_decomp_ranges_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--only-ranges', '0x0-0x2,0x7-0x9'
        )

        self.assert_decompilation_was_started_also_with(
            sel_decomp_ranges='0x0-0x2,0x7-0x9'
        )

    def test_sets_sel_decomp_decoding_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--decoding', 'only'
        )

        self.assert_decompilation_was_started_also_with(
            sel_decomp_decoding='only'
        )

    def test_sets_raw_endian_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--raw-endian', 'big'
        )

        self.assert_decompilation_was_started_also_with(
            raw_endian='big'
        )

    def test_sets_raw_entry_point_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--raw-entry-point', '0x8000'
        )

        self.assert_decompilation_was_started_also_with(
            raw_entry_point='0x8000'
        )

    def test_sets_raw_section_vma_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--raw-section-vma', '0x8000'
        )

        self.assert_decompilation_was_started_also_with(
            raw_section_vma='0x8000'
        )

    def test_generates_and_saves_cg_when_requested(self):
        self.call_main_with_standard_arguments_and(
            '--with-cg'
        )

        self.assert_decompilation_was_started_also_with(
            generate_cg=True
        )
        decompilation = self.get_started_decompilation()
        decompilation.wait_until_cg_is_generated.assert_called_once_with()
        decompilation.save_cg.assert_called_once_with(os.getcwd())

    def test_generates_and_saves_cfgs_when_requested(self):
        self.decompiler.start_decompilation().funcs_with_cfg = ['f1', 'f2']
        self.call_main_with_standard_arguments_and(
            '--with-cfgs'
        )

        self.assert_decompilation_was_started_also_with(
            generate_cfgs=True
        )
        decompilation = self.get_started_decompilation()
        decompilation.wait_until_cfg_is_generated.assert_any_call('f1')
        decompilation.save_cfg.assert_any_call('f1', os.getcwd())
        decompilation.wait_until_cfg_is_generated.assert_any_call('f2')
        decompilation.save_cfg.assert_any_call('f2', os.getcwd())

    def test_generates_and_saves_archive_when_requested(self):
        self.call_main_with_standard_arguments_and(
            '--with-archive'
        )

        self.assert_decompilation_was_started_also_with(
            generate_archive=True
        )
        decompilation = self.get_started_decompilation()
        decompilation.wait_until_archive_is_generated.assert_called_once_with()
        decompilation.save_archive.assert_called_once_with(os.getcwd())

    def test_saves_output_compiled_binary_when_mode_is_c(self):
        main([
            'decompiler.py',
            '--api-key', 'API-KEY',
            '--mode', 'c',
            'file'
        ])

        decompilation = self.get_started_decompilation()
        decompilation.save_binary.assert_called_once_with(os.getcwd())

    def test_saves_output_compiled_binary_when_input_is_c_file(self):
        main([
            'decompiler.py',
            '--api-key', 'API-KEY',
            'file.c'
        ])

        decompilation = self.get_started_decompilation()
        decompilation.save_binary.assert_called_once_with(os.getcwd())

    def test_saves_output_compiled_binary_when_input_is_c_file_uppercase_c(self):
        main([
            'decompiler.py',
            '--api-key', 'API-KEY',
            'file.C'
        ])

        decompilation = self.get_started_decompilation()
        decompilation.save_binary.assert_called_once_with(os.getcwd())

    def test_does_not_save_output_compiled_binary_when_mode_is_bin(self):
        main([
            'decompiler.py',
            '--api-key', 'API-KEY',
            '--mode', 'bin',
            'file'
        ])

        decompilation = self.get_started_decompilation()
        self.assertFalse(decompilation.save_binary.called)

    def test_does_not_save_output_compiled_binary_when_input_is_binary_file(self):
        main([
            'decompiler.py',
            '--api-key', 'API-KEY',
            'file.exe'
        ])

        decompilation = self.get_started_decompilation()
        self.assertFalse(decompilation.save_binary.called)

    def test_sends_pdb_file_when_given(self):
        self.call_main_with_standard_arguments_and(
            '--pdb-file', 'prog.pdb'
        )

        self.assert_decompilation_was_started_also_with(
            pdb_file='prog.pdb'
        )
