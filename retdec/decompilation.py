#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""A representation of decompilations."""

from retdec.exceptions import ArchiveGenerationFailedError
from retdec.exceptions import CFGGenerationFailedError
from retdec.exceptions import CGGenerationFailedError
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import NoSuchCFGError
from retdec.exceptions import OutputNotRequestedError
from retdec.resource import Resource


class DecompilationPhase:
    """Phase of a decompilation.

    :param str name: Name of the phase.
    :param str part: Part into which the phase belongs.
    :param str description: Description of the phase.
    :param int completion: What percentage of the decompilation has been
        completed?
    :param list warnings: A list of warnings that were produced by the
        decompiler in the phase. Each warning is a string.

    `part` may be ``None`` if the phase does not belong to any part.
    """

    def __init__(self, name, part, description, completion, warnings):
        self._name = name
        self._part = part
        self._description = description
        self._completion = completion
        self._warnings = warnings

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

    @property
    def warnings(self):
        """A list of warnings that were produced by the decompiler in the
        phase.

        Each warning is a string.
        """
        return self._warnings

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return ('{}(name={!r}, part={!r}, description={!r},'
                ' completion={}, warnings={!r})').format(
            __name__ + '.' + self.__class__.__name__,
            self.name,
            self.part,
            self.description,
            self.completion,
            self.warnings
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
        """Obtains and returns the list of phases
        (:class:`~retdec.decompilation.DecompilationPhase`).
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

    def cg_generation_has_finished(self):
        """Checks if the call-graph generation has finished.

        :raises OutputNotRequestedError: When the call graph was not requested
            to be generated.
        """
        self._update_state_if_needed()
        return self._cg_status.finished

    def cg_generation_has_succeeded(self):
        """Checks if the call-graph generation has succeeded.

        :raises OutputNotRequestedError: When the call graph was not requested
            to be generated.
        """
        self._update_state_if_needed()
        return self._cg_status.generated

    def cg_generation_has_failed(self):
        """Checks if the call graph has failed to generate.

        :raises OutputNotRequestedError: When the call graph was not requested
            to be generated.
        """
        self._update_state_if_needed()
        return self._cg_status.failed

    def get_cg_generation_error(self):
        """Returns the reason why the call graph failed to generate.

        :raises OutputNotRequestedError: When the call graph was not requested
            to be generated.

        If the call-graph generation has not failed, it returns ``None``.
        """
        self._update_state_if_needed()
        return self._cg_status.error

    def wait_until_cg_is_generated(
            self, on_failure=CGGenerationFailedError):
        """Waits until the call graph is generated.

        :param callable on_failure: What should be done when the generation
            fails?

        :raises OutputNotRequestedError: When the call graph was not requested
            to be generated.

        If `on_failure` is ``None``, nothing is done when the generation fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while not self.cg_generation_has_finished():
            self._wait_until_state_can_be_updated()

        if self._cg_status.failed:
            self._handle_failure(on_failure, self._cg_status.error)

    def save_cg(self, directory=None):
        """Saves the call graph to the given directory.

        :param str directory: Path to a directory in which the file will be
            stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('cg'),
            directory
        )

    @property
    def funcs_with_cfg(self):
        """A list of names of functions having a control-flow graph.

        The returned list does not depend on the control-flow-graph-generation
        status. It always returns the same function names, disregarding whether
        their control-flow graph has or has not been generated.

        The returned list is ordered by function names.

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        """
        self._update_state_if_needed()
        return sorted(self._cfg_statuses.keys())

    def cfg_generation_has_finished(self, func):
        """Checks if the generation of a control-flow graph for the given
        function has finished.

        :param str func: Name of the function.

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        :raises NoSuchCFGError: When there is no control-flow graph for the
            given function.
        """
        self._update_state_if_needed()
        return self._cfg_statuses[func].finished

    def cfg_generation_has_succeeded(self, func):
        """Checks if the generation of a control-flow graph for the given
        function has succeeded.

        :param str func: Name of the function.

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        :raises NoSuchCFGError: When there is no control-flow graph for the
            given function.
        """
        self._update_state_if_needed()
        return self._cfg_statuses[func].generated

    def cfg_generation_has_failed(self, func):
        """Checks if the generation of a control-flow graph for the given
        function has failed.

        :param str func: Name of the function.

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        :raises NoSuchCFGError: When there is no control-flow graph for the
            given function.
        """
        self._update_state_if_needed()
        return self._cfg_statuses[func].failed

    def get_cfg_generation_error(self, func):
        """Returns the reason why the control-flow graph for the given function
        failed to generate.

        :param str func: Name of the function.

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        :raises NoSuchCFGError: When there is no control-flow graph for the
            given function.

        If the control-flow-graph generation has not failed, it returns
        ``None``.
        """
        self._update_state_if_needed()
        return self._cfg_statuses[func].error

    def wait_until_cfg_is_generated(
            self, func, on_failure=CFGGenerationFailedError):
        """Waits until the control-flow graph for the given function is
        generated.

        :param str func: Name of the function.
        :param callable on_failure: What should be done when the generation
            fails?

        :raises OutputNotRequestedError: When control-flow graphs were not
            requested to be generated.
        :raises NoSuchCFGError: When there is no control-flow graph for the
            given function.

        If `on_failure` is ``None``, nothing is done when the generation fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while not self.cfg_generation_has_finished(func):
            self._wait_until_state_can_be_updated()

        if self._cfg_statuses[func].failed:
            self._handle_failure(on_failure, self._cfg_statuses[func].error)

    def save_cfg(self, func, directory=None):
        """Saves the control-flow graph for the given function to the given
        directory.

        :param str func: Name of the function.
        :param str directory: Path to a directory in which the file will be
            stored.

        :returns: Path to the saved file (`str`).

        If `directory` is ``None``, the current working directory is used.
        """
        return self._get_file_and_save_it(
            self._path_to_output_file('cfgs/{}'.format(func)),
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
        self._cg_status = self._cg_status_from_status(status)
        self._cfg_statuses = self._cfg_statuses_from_status(status)
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

    def _cg_status_from_status(self, status):
        """Returns the call-graph generation status from the given status."""
        if 'cg' not in status:
            return _NotRequestedOutputStatus()
        return _OutputGenerationStatus(**status['cg'])

    def _cfg_statuses_from_status(self, status):
        """Returns the control-flow-graph generation statuses from the given
        status.
        """
        if 'cfgs' not in status:
            return _DictRaisingOutputNotRequestedError()

        return _DictRaisingErrorWhenNoSuchCFG({
            func: _OutputGenerationStatus(**status)
            for func, status in status['cfgs'].items()
        })

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


class _DictRaisingOutputNotRequestedError(dict):
    """A dictionary that raises
    :class:`~retdec.exceptions.OutputNotRequestedError` upon access.
    """

    def keys(self):
        raise OutputNotRequestedError

    def __getitem__(self, key):
        raise OutputNotRequestedError


class _DictRaisingErrorWhenNoSuchCFG(dict):
    """A dictionary that raises :class:`~retdec.exceptions.NoSuchCFGError` when
    a key (i.e. a function) is missing.
    """

    def __missing__(self, func):
        raise NoSuchCFGError(func)
