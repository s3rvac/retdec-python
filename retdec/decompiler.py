#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the decompiler (decompilation of files)."""

import contextlib
import shutil

from retdec.file import File
from retdec.service import Service
from retdec.resource import Resource


class Decompiler(Service):
    """Access to the decompilation service."""

    def run_decompilation(self, **kwargs):
        """Starts a decompilation with the given arguments.

        :param input_file: File to be analyzed (**required**).
        :type input_file: str or file-like object
        :param mode: Decompilation mode.
        :type mode: str

        :returns: Started decompilation (:class:`Decompilation`).
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
        """Returns a mode from the given arguments (``dict``)."""
        if 'mode' in kwargs:
            return kwargs['mode'].lower()

        # Select the mode automatically based on the input file's name.
        if input_file.name.lower().endswith('.c'):
            return 'c'
        return 'bin'

    def _get_input_file(self, kwargs):
        """Returns an input file from the given arguments (``dict``)."""
        if 'input_file' in kwargs:
            return File(kwargs['input_file'])


class Decompilation(Resource):
    """A representation of a decompilation."""

    def save_output_hll(self):
        """Saves the decompiled output code to the current directory."""
        file_path = '/{}/outputs/hll'.format(self.id)
        with contextlib.closing(self._conn.get_file(file_path)) as src:
            with open(src.name, 'wb') as dst:
                shutil.copyfileobj(src, dst)
