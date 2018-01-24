#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tools that use the library to analyze and decompile files."""

from retdec import DEFAULT_API_URL
from retdec import __version__


def _add_arguments_shared_by_all_tools(parser):
    """Adds arguments that are used by all tools to the given parser."""
    parser.add_argument(
        '-k', '--api-key',
        dest='api_key',
        metavar='KEY',
        # It is important to set the API key to None by default because it
        # enables the use of the RETDEC_API_KEY environment variable.
        default=None,
        help='API key to be used.'
    )
    parser.add_argument(
        '-u', '--api-url',
        dest='api_url',
        metavar='URL',
        # It is important to set the URL to None by default because it enables
        # the use of the RETDEC_API_URL environment variable.
        default=None,
        help='URL to the API. Default: {}.'.format(DEFAULT_API_URL)
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s (via retdec-python) {}'.format(__version__)
    )
