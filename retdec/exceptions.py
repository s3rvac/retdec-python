#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Custom exceptions raised by the library."""


class RetdecError(Exception):
    """Base class of all custom exceptions raised by the library."""


class MissingAPIKeyError(RetdecError):
    """Exception raised when an API key is missing."""

    def __init__(self):
        super().__init__(
            'No explicit API key given'
            ' and environment variable RETDEC_API_KEY is not set.'
        )


class MissingParameterError(RetdecError):
    """Exception raised when a required parameter is not set.

    :param str name: Name of the missing parameter.
    """

    def __init__(self, name):
        super().__init__(
            "Missing parameter '{}'.".format(name)
        )


class InvalidValueError(RetdecError):
    """Exception raised when a parameter has an invalid value.

    :param str name: Name of the parameter whose value is invalid.
    :param value: The invalid value.
    """

    def __init__(self, name, value):
        super().__init__(
            "Value '{}' of parameter '{}' is invalid.".format(value, name)
        )


class AuthenticationError(RetdecError):
    """Exception raised when authentication with the provided API key fails."""

    def __init__(self):
        super().__init__(
            'Authentication with the given API key failed (is the key valid?).'
        )


class ConnectionError(RetdecError):
    """Exception raised when there is a connection error."""


class AnalysisFailedError(RetdecError):
    """Exception raised when a fileinfo analysis has failed."""


class DecompilationFailedError(RetdecError):
    """Exception raised when a decompilation has failed."""


class OutputNotRequestedError(RetdecError):
    """Exception raised when an output is queried which was not requested to be
    generated.
    """

    def __init__(self):
        super().__init__(
            'The output was not requested to be generated.'
        )


class CGGenerationFailedError(RetdecError):
    """Exception raised when the generation of a call graph fails.
    """


class CFGGenerationFailedError(RetdecError):
    """Exception raised when the generation of a control-flow graph fails."""


class NoSuchCFGError(RetdecError):
    """Exception raised when a control-flow graph for a non-existing function
    is requested.

    :param str func: Name of the function whose control-flow graph was
        requested.
    """

    def __init__(self, func):
        super().__init__(
            "There is no control-flow graph for '{}'.".format(func)
        )


class ArchiveGenerationFailedError(RetdecError):
    """Exception raised when the generation of an archive fails."""


class UnknownAPIError(RetdecError):
    """Exception raised when there is an unknown API error.

    :param int code: Error code.
    :param str message: Short message describing what went wrong.
    :param str description: Longer description of what went wrong.
    """

    def __init__(self, code, message, description):
        super().__init__(description)

        self._code = code
        self._message = message
        self._description = description

    @property
    def code(self):
        """Error code (`int`)."""
        return self._code

    @property
    def message(self):
        """Short message describing what went wrong (`str`)."""
        return self._message

    @property
    def description(self):
        """Longer description of what went wrong (`str`)."""
        return self._description
