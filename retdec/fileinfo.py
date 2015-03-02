#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the file-analyzing service (fileinfo)."""

import contextlib

from retdec.file import File
from retdec.service import Service
from retdec.resource import Resource


class Fileinfo(Service):
    """Access to the file-analyzing service."""

    def run_analysis(self, **kwargs):
        """Starts an analysis with the given arguments.

        :param input_file: File to be analyzed (**required**).
        :type input_file: str or file-like object
        :param verbose: Should the analysis produce a detailed output?
        :type verbose: bool

        :returns: Started analysis (:class:`Analysis`).
        """
        conn = self._create_new_api_connection('/fileinfo/analyses')
        id = self._start_analysis(conn, **kwargs)
        return Analysis(id, conn)

    def _start_analysis(self, conn, **kwargs):
        """Starts an analysis with the given arguments.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.

        :returns: Unique identifier of the analysis.
        """
        params = {
            'verbose': self._get_verbose_param(kwargs)
        }
        files = {
            'input': self._get_input_file(kwargs),
        }
        response = conn.send_post_request('', params=params, files=files)
        return response['id']

    def _get_verbose_param(self, kwargs):
        """Returns the value of the ``verbose`` parameter to be used when
        starting an analysis.
        """
        return self._get_param(
            'verbose',
            kwargs,
            default=False
        )

    def _get_input_file(self, kwargs):
        """Returns an input file from the given arguments (``dict``)."""
        if 'input_file' in kwargs:
            return File(kwargs['input_file'])


class Analysis(Resource):
    """A representation of an analysis."""

    def get_output(self):
        """Obtains and returns the output from the analysis."""
        file_path = '/{}/output'.format(self.id)
        with contextlib.closing(self._conn.get_file(file_path)) as file:
            return file.read().decode()
