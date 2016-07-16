#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""A representation of decompilations."""

from retdec.decompilation_phase import DecompilationPhase
from retdec.exceptions import ArchiveGenerationFailedError
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import OutputNotRequestedError
from retdec.resource import Resource


class Decompilation(Resource):
    """A representation of a decompilation."""

    def get_completion(self):
        """How much of the decompilation has been completed (in percentage)?

        It is an ``int`` between 0 and 100.
        """
        self._update_state_if_needed()
        return self._completion

    def get_phases(self):
        """Obtains and returns the list of phases
        (:class:`~retdec.decompilation_phase.DecompilationPhase`).
        """
        self._update_state_if_needed()
        return self._phases

    def wait_until_finished(self, callback=None,
                            on_failure=DecompilationFailedError):
        """Waits until the decompilation is finished.

        :param callable callback: Function to be called when the status of the
            decompilation is changed or when it finishes.
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

        if self._failed:
            self._handle_failure(on_failure, self._error)

    def get_hll_code(self):
        """Obtains and returns the decompiled code in the high-level language
        (`str`).
        """
        return self._get_file_contents(
            self._path_to_output_file('hll'),
            is_text_file=True
        )

    def save_hll_code(self, directory=None):
        """Saves the decompiled code in the high-level language to the given
        directory.

        :param str directory: Path to a directory in which the decompiled code
            will be stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('hll'),
            directory
        )

    def get_dsm_code(self):
        """Obtains and returns the disassembled input file in assembly-like
        syntax (`str`).
        """
        return self._get_file_contents(
            self._path_to_output_file('dsm'),
            is_text_file=True
        )

    def save_dsm_code(self, directory=None):
        """Saves the disassembled input file in assembly-like syntax to the
        given directory.

        :param str directory: Path to a directory in which the file will be
            stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('dsm'),
            directory
        )

    def archive_generation_has_finished(self):
        """Checks if the archive generation has finished.

        :raises OutputNotRequestedError: When the archive was not requested to
            be generated.
        """
        self._update_state_if_needed()
        return self._archive_status.finished

    def archive_generation_has_succeeded(self):
        """Checks if the archive generation has succeeded.

        :raises OutputNotRequestedError: When the archive was not requested to
            be generated.
        """
        self._update_state_if_needed()
        return self._archive_status.generated

    def archive_generation_has_failed(self):
        """Checks if the archive has failed to generate.

        :raises OutputNotRequestedError: When the archive was not requested to
            be generated.
        """
        self._update_state_if_needed()
        return self._archive_status.failed

    def get_archive_generation_error(self):
        """Returns the reason why the archive failed to generate.

        :raises OutputNotRequestedError: When the archive was not requested to
            be generated.

        If the archive has not failed, it returns ``None``.
        """
        self._update_state_if_needed()
        return self._archive_status.error

    def wait_until_archive_is_generated(
            self, on_failure=ArchiveGenerationFailedError):
        """Waits until the archive containing all outputs from the
        decompilation is generated.

        :param callable on_failure: What should be done when the generation
            fails?

        :raises OutputNotRequestedError: When the archive was not requested to
            be generated.

        If `on_failure` is ``None``, nothing is done when the generation fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while not self.archive_generation_has_finished():
            self._wait_until_state_can_be_updated()

        if self._archive_status.failed:
            self._handle_failure(on_failure, self._archive_status.error)

    def save_archive(self, directory=None):
        """Saves the archive containing all outputs from the decompilation
        to the given directory.

        :param str directory: Path to a directory in which the file will be
            stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('archive'),
            directory
        )

    def save_binary(self, directory=None):
        """Saves the compiled version of the input C file (provided that the
        input was a C file) to the given directory.

        :param str directory: Path to a directory in which the file will be
            stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('binary'),
            directory
        )

    def _update_state(self):
        """Updates the state of the decompilation."""
        status = super()._update_state()
        self._completion = status['completion']
        self._phases = self._phases_from_status(status)
        self._archive_status = self._archive_status_from_status(status)
        return status

    def _phases_from_status(self, status):
        """Creates a list of phases from the given status."""
        return [
            DecompilationPhase(
                phase['name'],
                phase['part'],
                phase['description'],
                phase['completion'],
                phase['warnings']
            ) for phase in status['phases']
        ]

    def _archive_status_from_status(self, status):
        """Returns the archive generation status from the given status."""
        if 'archive' not in status:
            return _NotRequestedOutputStatus()
        return _OutputGenerationStatus(**status['archive'])

    def _path_to_output_file(self, output_file):
        """Returns a path to the given output file."""
        return '/{}/outputs/{}'.format(self.id, output_file)

    def __repr__(self):
        return '<{} id={!r}>'.format(
            __name__ + '.' + self.__class__.__name__,
            self.id
        )


class _OutputGenerationStatus:
    """A status of output generation.

    :param bool generated: Has the output been generated?
    :param bool failed: Has the generation failed?
    :param str error: Reason why the generation failed.
    """

    def __init__(self, generated, failed, error):
        self._generated = generated
        self._failed = failed
        self._error = error

    @property
    def generated(self):
        """Has the output been generated?"""
        return self._generated

    @property
    def failed(self):
        """Has the generation failed?"""
        return self._failed

    @property
    def error(self):
        """Reason why the generation failed (`str`)."""
        return self._error

    @property
    def finished(self):
        """Has the output generation finished?"""
        return self.generated or self.failed


class _NotRequestedOutputStatus:
    """An output generation status that raises
    :class:`~retdec.exceptions.OutputNotRequestedError` whenever it is queried.
    """

    @property
    def generated(self):
        raise OutputNotRequestedError

    @property
    def failed(self):
        raise OutputNotRequestedError

    @property
    def error(self):
        raise OutputNotRequestedError

    @property
    def finished(self):
        raise OutputNotRequestedError
