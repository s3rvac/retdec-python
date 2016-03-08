#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""A representation of a fileinfo analysis."""

from retdec.exceptions import AnalysisFailedError
from retdec.resource import Resource


class Analysis(Resource):
    """A representation of a fileinfo analysis."""

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
        if self._failed:
            self._handle_failure(on_failure, self._error)

    def get_output(self):
        """Obtains and returns the output from the analysis (`str`)."""
        file_path = '/{}/output'.format(self.id)
        return self._get_file_contents(file_path, is_text_file=True)

    def __repr__(self):
        return '<{} id={!r}>'.format(
            __name__ + '.' + self.__class__.__name__,
            self.id
        )
