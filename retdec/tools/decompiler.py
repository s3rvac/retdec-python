#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
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

"""A tool for decompiling files. It uses the library."""

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
    def display_download_progress(self, file):
        """Displays progress of downloading the given file."""
        raise NotImplementedError

    def __repr__(self):
        return '<{}>'.format(self.__class__.__qualname__)


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

    def display_download_progress(self, file):
        # Do not display anything.
        pass


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
            'where the input file is located. For example, if the input file is '
            "'dir/prog.exe', then the decompiled code in the C language is "
            "saved as 'dir/prog.c'. You can override the output directory by "
            'using the -o/--output-dir parameter.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    _add_arguments_shared_by_all_tools(parser)
    parser.add_argument(
        '-m', '--mode',
        dest='mode',
        choices={'c', 'bin'},
        help='decompilation mode (default: automatic detection)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        dest='output_dir',
        help='save the outputs into this directory'
    )
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        help='print only errors, nothing else (not even progress)'
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        help='file to decompile'
    )
    return parser.parse_args(argv[1:])


def get_output_dir(input_file, output_dir):
    """Returns an absolute path to a directory where the output files should be
    saved.

    :param str input_file: Path to the input file from the tool parameters
                           (``args.file``).
    :param str output_dir: Path to the output directory from the tool
                           parameters (``args.output_dir``).
    """
    if output_dir is not None:
        # The output directory was forced by the user.
        return os.path.abspath(output_dir)

    # Save the outputs to the same directory where the input file is located.
    return os.path.abspath(os.path.dirname(input_file))


def get_progress_displayer(args):
    """Returns a proper progress displayer based on the arguments provided by
    the user.
    """
    if args.quiet:
        return NoProgressDisplayer()
    return ProgressBarDisplayer()


def main():
    args = parse_args(sys.argv)

    decompiler = Decompiler(
        api_url=args.api_url,
        api_key=args.api_key
    )

    decompilation = decompiler.run_decompilation(
        input_file=args.file,
        mode=args.mode
    )

    displayer = get_progress_displayer(args)
    displayer.display_decompilation_progress(decompilation)
    decompilation.wait_until_finished(
        callback=displayer.display_decompilation_progress
    )

    output_dir = get_output_dir(args.file, args.output_dir)
    decompilation.save_output_hll(output_dir)
    decompilation.save_output_dsm(output_dir)

    return 0


if __name__ == '__main__':
    sys.exit(main())
