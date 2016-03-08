#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tools that use the library to analyze and decompile files."""

from retdec import DEFAULT_API_URL


def _add_arguments_shared_by_all_tools(parser):
    """Adds arguments that are used by all tools to the given parser."""
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
