"""
    Access to the decompiler (decompilation of files).

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import contextlib
import shutil
import time

from retdec.file import File
from retdec.service import Service
from retdec.resource import Resource


class Decompiler(Service):
    """Access to the decompilation service."""

    def run_decompilation(self, **kwargs):
        """Starts a decompilation with the given arguments.

        :returns: Decompilation Started decompilation.
        """
        conn = self._create_new_api_connection('/decompiler/decompilations')
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


class Decompilation(Resource):
    """A representation of a decompilation."""

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
