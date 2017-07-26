#
# Project:   retdec-python
# Copyright: (c) 2015-2017 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the file-analyzing service (fileinfo)."""

from retdec.analysis import Analysis
from retdec.exceptions import MissingParameterError
from retdec.file import File
from retdec.service import Service


class Fileinfo(Service):
    """Access to the file-analyzing service."""

    def start_analysis(self, **kwargs):
        """Starts an analysis with the given parameters.

        :param input_file: File to be analyzed (**required**).
        :type input_file: str or file-like object
        :param output_format: Format of the output from the analysis.
        :type output_format: str
        :param verbose: Should the analysis produce a detailed output?
        :type verbose: bool

        :returns: Started analysis (:class:`~retdec.analysis.Analysis`).
        """
        conn = self._create_new_api_connection('/fileinfo/analyses')
        id = self._start_analysis(conn, kwargs)
        return Analysis(id, conn)

    def _start_analysis(self, conn, kwargs):
        """Starts an analysis with the given parameters.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
            for sending API requests.
        :param dict kwargs: Parameters for the analysis.

        :returns: Unique identifier of the analysis.
        """
        files = {
            'input': self._get_input_file(kwargs),
        }
        params = {}
        self._add_param_when_given('output_format', params, kwargs)
        self._add_param_when_given('verbose', params, kwargs)
        response = conn.send_post_request(files=files, params=params)
        return response['id']

    def _get_input_file(self, kwargs):
        """Returns the input file to be analyzed."""
        try:
            return File(kwargs['input_file'])
        except KeyError:
            raise MissingParameterError('input_file')

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            __name__ + '.' + self.__class__.__name__,
            self.api_url
        )
