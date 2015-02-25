"""
    A tool for decompiling files. It uses the library.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import argparse
import sys

from retdec import DEFAULT_API_URL
from retdec.decompiler import Decompiler


def parse_args(argv):
    """Parses the given list of arguments."""
    parser = argparse.ArgumentParser(
        description=('Decompiles the given file through the retdec.com '
                     'decompilation service by using their public REST API.')
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        help='file to decompile'
    )
    parser.add_argument(
        '-k', '--api-key',
        dest='api_key',
        metavar='KEY',
        help='API key to be used'
    )
    parser.add_argument(
        '-u', '--api-url',
        dest='api_url',
        metavar='URL',
        default=DEFAULT_API_URL,
        help='URL to the API (default: {})'.format(DEFAULT_API_URL)
    )
    return parser.parse_args(argv[1:])


def main():
    args = parse_args(sys.argv)
    decompiler = Decompiler(api_url=args.api_url, api_key=args.api_key)
    decompilation = decompiler.run_decompilation(input_file=args.file)
    decompilation.wait_until_finished()
    decompilation.save_output_hll()
    return 0


if __name__ == '__main__':
    sys.exit(main())
