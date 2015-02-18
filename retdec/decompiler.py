"""
    retdec.decompiler
    ~~~~~~~~~~~~~~~~~

    Access to the decompiler (decompilation of files).

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import os

from retdec import DEFAULT_API_URL
from retdec.exceptions import MissingAPIKeyError


class Decompiler:
    """Access to the decompiler (decompilation of files)."""

    def __init__(self, *, api_key=None, api_url=None):
        """Initializes the decompiler.

        :param str api_key: API key to be used for authentication.
        :param str api_url: URL to the API.
        """
        self._api_key = self._get_api_key_to_use(api_key)
        self._api_url = self._get_api_url_to_use(api_url)

    @property
    def api_key(self):
        """API key that is being used for authentication (`str`)."""
        return self._api_key

    @property
    def api_url(self):
        """URL to the API (`str`)."""
        return self._api_url

    @staticmethod
    def _get_api_key_to_use(api_key):
        """Returns an API key to be used based on the given key and environment
        variables.

        :raises MissingAPIKeyError: When no API key is available.
        """
        if api_key is not None:
            return api_key

        try:
            return os.environ['RETDEC_API_KEY']
        except KeyError:
            raise MissingAPIKeyError from None

    @staticmethod
    def _get_api_url_to_use(api_url):
        """Returns an API URL to be used based on the given URL and environment
        variables.
        """
        if api_url is None:
            api_url = os.environ.get('RETDEC_API_URL', DEFAULT_API_URL)

        # Ensure that the URL does not end with a slash.
        return api_url.rstrip('/')
