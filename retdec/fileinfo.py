#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the file-analyzing service (fileinfo)."""

from retdec.exceptions import AnalysisFailedError
from retdec.file import File
from retdec.resource import Resource
from retdec.service import Service


class Fileinfo(Service):
    """Access to the file-analyzing service."""

    def run_analysis(self, **kwargs):
        """Starts an analysis with the given parameters.

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
        """Starts an analysis with the given parameters.

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

    def _get_verbose_param(self, params):
        """Returns the value of the ``verbose`` parameter to be used when
        starting an analysis.
        """
        return self._get_param(
            'verbose',
            params,
            default=False
        )

    def _get_input_file(self, params):
        """Returns an input file from the given parameters (``dict``)."""
        if 'input_file' in params:
            return File(params['input_file'])

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            __name__ + '.' + self.__class__.__qualname__,
            self.api_url
        )


class Analysis(Resource):
    """A representation of an analysis."""

    def wait_until_finished(self, on_failure=AnalysisFailedError):
        """Waits until the analysis is finished.

        :param callable on_failure: What should be done when the analysis
                                    fails?

        If `on_failure` is ``None``, nothing is done when the analysis fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while not self.has_finished():
            self._wait_until_state_can_be_updated()

        # The analysis has finished.
        if self._failed and on_failure is not None:
            obj = on_failure(self._error)
            if isinstance(obj, Exception):
                raise obj

    def get_output(self):
        """Obtains and returns the output from the analysis (`str`)."""
        file_path = '/{}/output'.format(self.id)
        return self._get_file_contents(file_path, is_text_file=True)
