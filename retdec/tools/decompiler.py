#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""A tool for decompiling files. It uses the library."""

import argparse
import sys

from retdec.decompiler import Decompiler
from retdec.tools import _add_arguments_shared_by_all_tools


def parse_args(argv):
    """Parses the given list of arguments."""
    parser = argparse.ArgumentParser(
        description=('Decompiles the given file through the retdec.com '
                     'decompilation service by using their public REST API.')
    )
    _add_arguments_shared_by_all_tools(parser)
    parser.add_argument(
        '-m', '--mode',
        dest='mode',
        choices={'c', 'bin'},
        help='decompilation mode (default: automatic detection)'
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        help='file to decompile'
    )
    return parser.parse_args(argv[1:])


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
    decompilation.save_output_hll()
    return 0


if __name__ == '__main__':
    sys.exit(main())
