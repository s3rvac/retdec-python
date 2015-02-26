"""
    Access to the file-analyzing service (fileinfo).

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

import contextlib

from retdec.file import File
from retdec.service import Service
from retdec.resource import Resource


class Fileinfo(Service):
    """Access to the file-analyzing service."""

    def run_analysis(self, **kwargs):
        """Starts a analysis with the given arguments.

        :returns: Started analysis (:class:`Analysis`).
        """
        conn = self._create_new_api_connection('/fileinfo/analyses')
        id = self._start_analysis(conn, **kwargs)
        return Analysis(id, conn)

    def _start_analysis(self, conn, **kwargs):
        """Starts a analysis with the given arguments.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.

        :returns: Unique identifier of the analysis.
        """
        files = {
            'input': self._get_input_file(kwargs)
        }
        response = conn.send_post_request('', files=files)
        return response['id']

    def _get_input_file(self, kwargs):
        """Returns an input file from the given arguments (``dict``)."""
        if 'input_file' in kwargs:
            return File(kwargs['input_file'])


class Analysis(Resource):
    """A representation of a analysis."""

    def get_output(self):
        """Obtains and returns the output from the analysis."""
        file_path = '/{}/output'.format(self.id)
        with contextlib.closing(self._conn.get_file(file_path)) as file:
            return file.read().decode()
