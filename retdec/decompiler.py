#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the decompiler (decompilation of files)."""

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

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            __name__ + '.' + self.__class__.__qualname__,
            self.api_url
        )


class DecompilationPhase:
    """Phase of a decompilation."""

    def __init__(self, name, part, description, completion):
        """Initializes a phase."""
        self._name = name
        self._part = part
        self._description = description
        self._completion = completion

    @property
    def name(self):
        """Name of the phase (`str`)."""
        return self._name

    @property
    def part(self):
        """Part to which the phase belongs (`str`).

        May be ``None`` if the phase does not belong to any part.
        """
        return self._part

    @property
    def description(self):
        """Description of the phase (`str`)."""
        return self._description

    @property
    def completion(self):
        """Completion (in percentages, ``0-100``)."""
        return self._completion

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '{}(name={!r}, part={!r}, description={!r}, completion={})'.format(
            __name__ + '.' + self.__class__.__qualname__,
            self.name,
            self.part,
            self.description,
            self.completion
        )


class Decompilation(Resource):
    """A representation of a decompilation."""

    def get_completion(self):
        """How much of the decompilation has been completed (in percentage)?

        It is an ``int`` between 0 and 100.
        """
        self._update_state_if_needed()
        return self._completion

    def get_phases(self):
        """Obtains and returns a list of phases.

        The returned type is a list of
        :class:`retdec.decompiler.DecompilationPhase`.
        """
        self._update_state_if_needed()
        return self._phases

    def wait_until_finished(self, callback=None,
                            on_failure=DecompilationFailedError):
        """Waits until the decompilation is finished.

        :param callable callback: Function to be called when the status of the
                                  decompilation is changed or it finishes.
        :param callable on_failure: What should be done when the decompilation
                                    fails?

        If `callback` is not ``None``, it is called with the decompilation as
        its argument when the status of the decompilation is changed or when it
        finishes.

        If `on_failure` is ``None``, nothing is done when the decompilation
        fails. Otherwise, it is called with the error message. If the returned
        value is an exception, it is raised.
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
        # decompilation may have immediately finished, without giving us chance
        # to call the callback.
        callback(self)

        if self._failed and on_failure is not None:
            obj = on_failure(self._error)
            if isinstance(obj, Exception):
                raise obj

    def get_output_hll(self):
        """Obtains and returns the decompiled code in the high-level language
        (`str`).
        """
        return self._get_file_contents(
            self._path_to_output_file('hll'),
            is_text_file=True
        )

    def save_output_hll(self, directory=None):
        """Saves the decompiled code in the high-level language to the given
        directory.

        :param str directory: Path to a directory in which the decompiled
                              output will be stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it_to(
            self._path_to_output_file('hll'),
            directory
        )

    def get_output_dsm(self):
        """Obtains and returns the disassembled input file in assembly-like
        syntax (`str`).
        """
        return self._get_file_contents(
            self._path_to_output_file('dsm'),
            is_text_file=True
        )

    def save_output_dsm(self, directory=None):
        """Saves the disassembled input file in assembly-like syntax to the
        given directory.

        :param str directory: Path to a directory in which the file will be
                              stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it_to(
            self._path_to_output_file('dsm'),
            directory
        )

    def _update_state(self):
        """Updates the state of the decompilation."""
        status = super()._update_state()
        self._completion = status['completion']
        self._phases = self._phases_from_status(status)
        return status

    def _phases_from_status(self, status):
        """Creates a list of phases from the given status."""
        return [DecompilationPhase(**phase) for phase in status['phases']]

    def _path_to_output_file(self, output_file):
        """Returns a path to the given output file."""
        return '/{}/outputs/{}'.format(self.id, output_file)

    def __repr__(self):
        return '<{} id={!r}>'.format(
            __name__ + '.' + self.__class__.__qualname__,
            self.id
        )
