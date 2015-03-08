#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""A tool for decompiling files. It uses the library."""

import argparse
import os
import sys

from retdec.decompiler import Decompiler
from retdec.tools import _add_arguments_shared_by_all_tools


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
    decompilation.wait_until_finished()
    output_dir = get_output_dir(args.file, args.output_dir)
    decompilation.save_output_hll(output_dir)
    decompilation.save_output_dsm(output_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
