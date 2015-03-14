#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Base class of all services."""

import os

from retdec import DEFAULT_API_URL
from retdec.conn import APIConnection
from retdec.exceptions import InvalidValueError
from retdec.exceptions import MissingAPIKeyError
from retdec.exceptions import MissingParameterError


class Service:
    """Base class of all services."""

    def __init__(self, *, api_key=None, api_url=None):
        """Initializes the service.

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

    def _create_new_api_connection(self, path):
        """Creates a new API connection from the given path.

        :param str path: Path that is appended after the API URL.
        """
        return APIConnection(self.api_url + path, self.api_key)

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

        # Ensure that the URL does not end with a slash because the API does
        # not use trailing slashes.
        return api_url.rstrip('/')

    @staticmethod
    def _get_param(name, params, required=False, choices=None, default=None):
        """Returns the value of the given parameter.

        :param str name: Name of the parameter.
        :param dict params: Parameters from which the value should be obtained.
        :param bool required: Has the parameter be present and be non-``None``?
        :param set choices: Allowed values for the parameter.
        :param object default: Default value to return when `required` is
                               ``False`` and the parameter is not found.
        """
        if name not in params or params[name] is None:
            if required:
                raise MissingParameterError(name)
            return default

        value = params[name]

        if choices is not None and value not in choices:
            raise InvalidValueError(name, value)

        return value
