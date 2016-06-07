#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Base class of all services."""

import os

from retdec import DEFAULT_API_URL
from retdec.conn import APIConnection
from retdec.exceptions import InvalidValueError
from retdec.exceptions import MissingAPIKeyError


class Service:
    """Base class of all services.

    :param str api_key: API key to be used for authentication.
    :param str api_url: URL to the API.
    """

    def __init__(self, *, api_key=None, api_url=None):
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

    def _create_new_api_connection(self, path):
        """Creates a new API connection from the given path.

        :param str path: Path that is appended after the API URL.
        """
        return APIConnection(self.api_url + path, self.api_key)

    @staticmethod
    def _get_api_key_to_use(api_key):
        """Returns an API key to be used based on the given key and environment
        variables.
        """
        if api_key is not None:
            return api_key

        api_key = os.environ.get('RETDEC_API_KEY', None)
        if api_key is not None:
            return api_key

        raise MissingAPIKeyError

    @staticmethod
    def _get_api_url_to_use(api_url):
        """Returns an API URL to be used based on the given URL and environment
        variables.
        """
        if api_url is None:
            api_url = os.environ.get('RETDEC_API_URL', DEFAULT_API_URL)

        # Ensure that the URL does not end with a slash because the API does
        # not use trailing slashes.
        return api_url.rstrip('/')

    @staticmethod
    def _get_param(name, params, choices=None, default=None):
        """Returns the value of the given parameter.

        :param str name: Name of the parameter.
        :param dict params: Parameters from which the value should be obtained.
        :param set choices: Allowed values for the parameter.
        :param object default: Default value to return when the parameter is
            not found.
        """
        if name not in params or params[name] is None:
            return default

        value = params[name]

        if choices is not None and value not in choices:
            raise InvalidValueError(name, value)

        return value
