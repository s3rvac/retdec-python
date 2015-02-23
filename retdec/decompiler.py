"""
    retdec.decompiler
    ~~~~~~~~~~~~~~~~~

    Access to the decompiler (decompilation of files).

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import contextlib
import os
import shutil
import time

from retdec import DEFAULT_API_URL
from retdec.conn import APIConnection
from retdec.exceptions import MissingAPIKeyError
from retdec.file import File


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

    def run_decompilation(self, **kwargs):
        """Starts a decompilation with the given arguments.

        :returns: Decompilation Started decompilation.
        """
        conn = APIConnection(
            self.api_url + '/decompiler/decompilations',
            self.api_key
        )
        id = self._start_decompilation(conn, **kwargs)
        return Decompilation(id, conn)

    def _start_decompilation(self, conn, **kwargs):
        """Starts a decompilation with the given arguments.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.

        :returns: Unique identifier of the decompilation.
        """
        # The input file is always required.
        input_file = self._get_input_file(kwargs)

        params = {
            'mode': self._get_mode(input_file, kwargs)
        }
        files = {
            'input': input_file
        }
        response = conn.send_post_request('', params=params, files=files)
        return response['id']

    def _get_mode(self, input_file, kwargs):
        """Returns a mode from the given arguments (`dict`)."""
        if 'mode' in kwargs:
            return kwargs['mode'].lower()

        # Select the mode automatically based on the input file's name.
        if input_file.name.lower().endswith('.c'):
            return 'c'
        return 'bin'

    def _get_input_file(self, kwargs):
        """Returns an input file from the given arguments (`dict`)."""
        if 'input_file' in kwargs:
            return File(kwargs['input_file'])

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

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            self.__class__.__qualname__,
            self.api_url
        )


class Decompilation:
    """A representation of a decompilation."""

    def __init__(self, id, conn):
        """Initializes a decompilation.

        :param str id: Unique identifier of the decompilation.
        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.
        """
        self._id = id
        self._conn = conn

    @property
    def id(self):
        """Unique identifier of the decompilation."""
        return self._id

    def wait_until_finished(self):
        """Waits until the decompilation finishes."""
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while True:
            response = self._conn.send_get_request('/{}/status'.format(self.id))
            if response['finished']:
                break
            # Sleep a bit to prevent abuse of the API.
            time.sleep(0.5)

    def save_output_hll(self):
        """Saves the decompiled output code to the current directory."""
        file_path = '/{}/outputs/hll'.format(self.id)
        with contextlib.closing(self._conn.get_file(file_path)) as src:
            with open(src.name, 'wb') as dst:
                shutil.copyfileobj(src, dst)
