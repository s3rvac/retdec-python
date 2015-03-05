#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the decompiler (decompilation of files)."""

import contextlib
import shutil

from retdec.exceptions import DecompilationFailedError
from retdec.file import File
from retdec.resource import Resource
from retdec.service import Service


class Decompiler(Service):
    """Access to the decompilation service."""

    def run_decompilation(self, **kwargs):
        """Starts a decompilation with the given parameters.

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
        """Starts a decompilation with the given parameters.

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

    def _get_mode(self, input_file, params):
        """Returns a mode from the given parameters (``dict``)."""
        return self._get_param(
            'mode',
            params,
            choices={'c', 'bin'},
            default=self._get_default_mode(input_file)
        )

    def _get_default_mode(self, input_file):
        """Returns a default mode to be used based on the given input file's
        name.
        """
        return 'c' if input_file.name.lower().endswith('.c') else 'bin'

    def _get_input_file(self, params):
        """Returns an input file from the given parameters (``dict``)."""
        if 'input_file' in params:
            return File(params['input_file'])


class Decompilation(Resource):
    """A representation of a decompilation."""

    def get_completion(self):
        """How much of the resource has been completed?

        It is an ``int`` between 0 and 100.
        """
        self._update_state_if_needed()
        return self._completion

    def wait_until_finished(self, callback=None,
                            on_failure=DecompilationFailedError):
        """Waits until the decompilation is finished.

        :param callable callback: Function to be called when the status of the
                                  decompilation is changed or it finishes.
        :param callable on_failure: What should be done when the decompilation
                                    fails?

        If `callback` is not ``None``, it is called with the decompilation as its
        argument when the status of the decompilation is changed or when it
        finishes.

        If `on_failure` is ``None``, nothing is done when the decompilation fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Ensure that we have something callable (do nothing by default).
        callback = callback or (lambda _: None)

        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        # Track completion changes so we can call the callback when the status
        # changes.
        last_completion = None
        while not self.has_finished():
            if (last_completion is not None and
                    self._completion != last_completion):
                callback(self)
            last_completion = self._completion

            self._wait_until_state_can_be_updated()

        # The decompilation has finished.

        # Call the callback one final time. This has to be done because the
        # decompilation may have immediately finished, without giving us chance to
        # call the callback.
        callback(self)

        if self._failed and on_failure is not None:
            obj = on_failure(self._error)
            if isinstance(obj, Exception):
                raise obj

    def save_output_hll(self):
        """Saves the decompiled output code to the current directory."""
        file_path = '/{}/outputs/hll'.format(self.id)
        with contextlib.closing(self._conn.get_file(file_path)) as src:
            with open(src.name, 'wb') as dst:
                shutil.copyfileobj(src, dst)

    def _update_state(self):
        """Updates the state of the decompilation."""
        status = super()._update_state()
        self._completion = status['completion']
        return status
