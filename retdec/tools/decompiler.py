#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# The progress displayers are based on the following script:
#
#     https://retdec.com/api/scripts/decompile.py
#
#     Copyright (c) 2015 AVG Technologies.
#
#     Distributed under the MIT license:
#
#     Permission is hereby granted, free of charge, to any person obtaining a
#     copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to the
#     following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#

"""A tool for decompilation of files. It uses the library."""

import abc
import argparse
import os
import sys

from retdec.decompiler import Decompiler
from retdec.tools import _add_arguments_shared_by_all_tools


class ProgressDisplayer(metaclass=abc.ABCMeta):
    """Base class of progress displayers."""

    @abc.abstractmethod
    def display_decompilation_progress(self, d):
        """Displays or updates progress of the given decompilation."""
        raise NotImplementedError

    @abc.abstractmethod
    def display_download_progress(self, file_name):
        """Displays progress of downloading file with the given name."""
        raise NotImplementedError

    def __repr__(self):
        return '<{}>'.format(
            __name__ + '.' + self.__class__.__name__
        )


class ProgressBarDisplayer(ProgressDisplayer):
    """Displays a progress bar during decompilation."""

    #: Length of the progress bar (in characters).
    BAR_LENGTH = 40

    #: Character to be used as the fill symbol.
    BAR_FILL_CHAR = '#'

    #: Character to be used as the empty symbol.
    BAR_EMPTY_CHAR = ' '

    def display_decompilation_progress(self, d):
        # Example:
        #
        #     8DRerEdKop: [##################  ] 85%
        #

        completion = d.get_completion()
        fill_length = int(self.BAR_LENGTH * (completion / 100))

        # '\r' causes the current line to be overwritten.
        sys.stdout.write('\r{}: [{}{}] {}% '.format(
            d.id,
            self.BAR_FILL_CHAR * fill_length,
            self.BAR_EMPTY_CHAR * (self.BAR_LENGTH - fill_length),
            completion
        ))

        if d.has_finished():
            if d.has_succeeded():
                sys.stdout.write('OK')
            else:
                sys.stdout.write('FAIL')
            sys.stdout.write('\n')

        # Make the output available as soon as possible.
        sys.stdout.flush()

    def display_download_progress(self, file_name):
        # Do not display anything.
        pass


class ProgressLogDisplayer(ProgressDisplayer):
    """Displays a progress log during decompilation."""

    def __init__(self):
        self._phases = []
        self._last_part = None
        self._last_phase_index = 0
        self._prologue_printed = False
        self._first_download = True

    def display_decompilation_progress(self, d):
        # Example:
        #
        #    8DRerEdKop
        #    ----------
        #
        #    Waiting for resources (0%)...                 [OK]
        #    Pre-Processing:
        #      Obtaining file information (5%)...          [OK]
        #    Front-End:
        #      Initializing (20%)...                       [OK]
        #      Creating instruction decoders (22%)...      [OK]
        #      Detecting statically linked code (25%)...   [OK]
        #      Instruction decoding (28%)...               [OK]
        #      Control-flow analysis (31%)...              [OK]
        #      Data-flow analysis (34%)...                 [OK]
        #      Type recovery (37%)...                      [OK]
        #      Generating LLVM IR (40%)...                 [OK]
        #    Middle-End:
        #      Initializing (45%)...                       [OK]
        #      Validating the LLVM IR (50%)...             [OK]
        #      Optimizing the LLVM IR (55%)...             [OK]
        #    Back-End:
        #      Initializing (60%)...                       [OK]
        #      Converting the LLVM IR into BIR (65%)...    [OK]
        #      Optimizing the BIR (70%)...                 [OK]
        #      Validating the BIR (90%)...                 [OK]
        #      Generating the target code (95%)...         [OK]
        #    Done (100%)...
        #

        self._print_prologue_unless_already_printed(d)

        self._print_phases(self._get_new_phases(d))

        if d.has_finished():
            self._print_decompilation_end(d)
            self._print_warnings_in_last_phase()

        # Make the output available as soon as possible.
        sys.stdout.flush()

    def _print_prologue_unless_already_printed(self, d):
        """Prints the prologue unless it has already been printed."""
        if not self._prologue_printed:
            self._print_prologue(d)
            self._prologue_printed = True

    def _print_prologue(self, d):
        """Prints the prologue."""
        prologue = '{}'.format(d.id)
        sys.stdout.write('{}\n'.format(prologue))
        sys.stdout.write('{}\n'.format('-' * len(prologue)))
        sys.stdout.write('\n')

    def _get_new_phases(self, d):
        """Returns new phases from the given decompilation."""
        self._phases = d.get_phases()
        return self._phases[self._last_phase_index:]

    def _print_phases(self, phases):
        """Prints the given phases."""
        for phase in phases:
            # Print status and warnings for the last phase (if any).
            if self._last_phase_index > 0:
                self._print_end_of_successful_phase()
                self._print_warnings_in_last_phase()
            self._print_phase(phase)
            self._last_part = phase.part
            self._last_phase_index += 1

    def _print_phase(self, phase):
        """Prints the given phase."""
        phase_str = ''

        if phase.part is not None:
            if phase.part != self._last_part:
                # Entering a new part.
                sys.stdout.write('{}:\n'.format(phase.part))
            phase_str += '  '

        phase_str += '{} ({}%)...'.format(phase.description, phase.completion)

        # Print the phase in an aligned way so the status can be printed
        # afterwards. The number below has been chosen experimentally based on
        # the longest phase string that we can have.
        sys.stdout.write('{0:<50} '.format(phase_str))

    def _print_decompilation_end(self, d):
        """Prints the end of the decompilation."""
        if d.has_failed():
            self._print_end_of_failed_phase()
        else:
            # Do not print '[OK]' for the last phase ('Done'), just end the
            # line.
            sys.stdout.write('\n')

    def _print_end_of_successful_phase(self):
        """Prints the and of a successful phase."""
        self._print_phase_end('OK')

    def _print_end_of_failed_phase(self):
        """Prints the and of a failed phase."""
        self._print_phase_end('FAIL')

    def _print_phase_end(self, status):
        """Prints the end of the current phase."""
        sys.stdout.write('[{}]\n'.format(status))

    def _print_warnings_in_last_phase(self):
        """Prints warnings from the last phase (if any)."""
        if self._last_phase_index:
            last_phase = self._phases[self._last_phase_index - 1]
            self._print_warnings_in_phase(last_phase)

    def _print_warnings_in_phase(self, phase):
        """Prints warnings from the given phase (if any)."""
        for warning in phase.warnings:
            self._print_warning(warning)

    def _print_warning(self, warning):
        """Prints the given warning."""
        sys.stdout.write('Warning: {}\n'.format(warning))

    def display_download_progress(self, file_name):
        # Example:
        #
        #    Downloading:
        #     - prog.c
        #     - prog.dsm
        #

        self._print_download_header_unless_already_printed()

        sys.stdout.write(' - {}\n'.format(file_name))

        # Make the output available as soon as possible.
        sys.stdout.flush()

    def _print_download_header_unless_already_printed(self):
        """Prints the "downloading" header (unless it has been already
        printed).
        """
        if self._first_download:
            sys.stdout.write('\nDownloading:\n')
            self._first_download = False


class NoProgressDisplayer(ProgressDisplayer):
    """Displays nothing."""

    def display_decompilation_progress(self, d):
        pass

    def display_download_progress(self, file):
        pass


def parse_args(argv):
    """Parses the given list of arguments."""
    parser = argparse.ArgumentParser(
        description=(
            'Decompiles the given file through the retdec.com '
            'decompilation service by using their public REST API.\n'
            '\n'
            'By default, the output files are stored into the same directory '
            'where the input file is located. For example, if the input file '
            "is 'dir/prog.exe', then the decompiled code in the C language is "
            "saved as 'dir/prog.c'. You can override the output directory by "
            'using the -o/--output-dir parameter.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    _add_arguments_shared_by_all_tools(parser)
    parser.add_argument(
        '-a', '--architecture',
        dest='architecture',
        choices=['x86', 'arm', 'thumb', 'mips', 'pic32', 'powerpc'],
        help='architecture to force when (de)compiling'
    )
    parser.add_argument(
        '-b', '--brief',
        dest='brief',
        action='store_true',
        help='print fewer information during the decompilation'
    )
    parser.add_argument(
        '-c', '--compiler',
        dest='comp_compiler',
        choices=['gcc', 'clang'],
        help='compiler to be used when compiling'
    )
    parser.add_argument(
        '-C', '--compiler-optimizations',
        dest='comp_optimizations',
        choices=['O0', 'O1', 'O2', 'O3'],
        help='compiler optimizations to be used when compiling'
    )
    parser.add_argument(
        '-g', '--compiler-debug',
        dest='comp_debug',
        action='store_true',
        default=None,
        help='compile the input C file with debugging information'
    )
    parser.add_argument(
        '-s', '--compiler-strip',
        dest='comp_strip',
        action='store_true',
        default=None,
        help='strip the compiled C file prior its decompilation'
    )
    parser.add_argument(
        '-f', '--file-format',
        dest='file_format',
        choices=['elf', 'pe'],
        help='file format to force when compiling'
    )
    parser.add_argument(
        '-l', '--target-language',
        dest='target_language',
        choices=['c', 'py'],
        help='target high-level language'
    )
    parser.add_argument(
        '-m', '--mode',
        dest='mode',
        choices=['c', 'bin'],
        help='decompilation mode (default: automatic detection)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        dest='output_dir',
        metavar='DIR',
        help='save the outputs into this directory'
    )
    parser.add_argument(
        '-p', '--pdb-file',
        dest='pdb_file',
        metavar='FILE',
        help='PDB file associated with the input file'
    )
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        help='print only errors, nothing else (not even progress)'
    )
    parser.add_argument(
        '--with-archive',
        dest='generate_archive',
        action='store_true',
        default=None,
        help='generate an archive containing all decompilation outputs'
    )
    parser.add_argument(
        'input_file',
        metavar='FILE',
        help='file to decompile'
    )
    return parser.parse_args(argv[1:])


def get_output_dir(args):
    """Returns an absolute path to a directory where the output files should be
    saved.
    """
    if args.output_dir is not None:
        # The output directory was forced by the user.
        return os.path.abspath(args.output_dir)

    # Save the outputs to the same directory where the input file is located.
    return os.path.abspath(os.path.dirname(args.input_file))


def get_progress_displayer(args):
    """Returns a proper progress displayer based on the arguments provided by
    the user.
    """
    if args.quiet:
        return NoProgressDisplayer()
    elif args.brief:
        return ProgressBarDisplayer()
    return ProgressLogDisplayer()


def display_download_progress(displayer, file_path):
    """Displays progress of downloading the given file."""
    displayer.display_download_progress(os.path.basename(file_path))


def add_decompilation_param_when_given(args, params, param_name):
    """Adds a parameter with `param_name` from `args` to `params`, provided
    that the parameter is set.
    """
    param_value = getattr(args, param_name)
    if param_value is not None:
        params[param_name] = param_value


def should_download_output_binary_file(args):
    """Should the compiled version of the input C file be downloaded?
    """
    # It should be downloaded only when we are decompiling a C file.
    if args.mode == 'c':
        return True
    elif not args.mode and args.input_file.lower().endswith('c'):
        return True
    return False


def main(argv=None):
    """Runs the tool.

    :param list argv: Tool arguments.

    If `argv` is ``None``, ``sys.argv`` is used.
    """
    args = parse_args(argv if argv is not None else sys.argv)

    decompiler = Decompiler(
        api_url=args.api_url,
        api_key=args.api_key
    )

    params = {}
    add_decompilation_param_when_given(args, params, 'input_file')
    add_decompilation_param_when_given(args, params, 'pdb_file')
    add_decompilation_param_when_given(args, params, 'mode')
    add_decompilation_param_when_given(args, params, 'target_language')
    add_decompilation_param_when_given(args, params, 'architecture')
    add_decompilation_param_when_given(args, params, 'file_format')
    add_decompilation_param_when_given(args, params, 'comp_compiler')
    add_decompilation_param_when_given(args, params, 'comp_optimizations')
    add_decompilation_param_when_given(args, params, 'comp_debug')
    add_decompilation_param_when_given(args, params, 'comp_strip')
    add_decompilation_param_when_given(args, params, 'generate_archive')
    decompilation = decompiler.start_decompilation(**params)

    displayer = get_progress_displayer(args)
    displayer.display_decompilation_progress(decompilation)
    decompilation.wait_until_finished(
        callback=displayer.display_decompilation_progress
    )

    output_dir = get_output_dir(args)

    file_path = decompilation.save_hll_code(output_dir)
    display_download_progress(displayer, file_path)

    file_path = decompilation.save_dsm_code(output_dir)
    display_download_progress(displayer, file_path)

    if should_download_output_binary_file(args):
        file_path = decompilation.save_binary(output_dir)
        display_download_progress(displayer, file_path)

    if args.generate_archive:
        decompilation.wait_until_archive_is_generated()
        file_path = decompilation.save_archive(output_dir)
        display_download_progress(displayer, file_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
