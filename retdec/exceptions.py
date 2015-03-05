#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
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
    """Exception raised when a required parameter is not set."""

    def __init__(self, name):
        super().__init__(
            "Missing parameter '{}'.".format(name)
        )


class InvalidValueError(RetdecError):
    """Exception raised when a parameter has an invalid value."""

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

    def __init__(self, reason=None):
        message = 'Connection to the API failed.'
        if reason is not None:
            message += ' Reason: {}'.format(reason)
        super().__init__(message)


class AnalysisFailedError(RetdecError):
    """Exception raised when a fileinfo analysis has failed."""

    def __init__(self, reason=None):
        message = 'The analysis has failed.'
        if reason is not None:
            message += ' Reason: {}'.format(reason)
        super().__init__(message)


class DecompilationFailedError(RetdecError):
    """Exception raised when a decompilation has failed."""

    def __init__(self, reason=None):
        message = 'The decompilation has failed.'
        if reason is not None:
            message += ' Reason: {}'.format(reason)
        super().__init__(message)


class UnknownAPIError(RetdecError):
    """Exception raised when there is an unknown API error.

    :ivar int code: Error code.
    :ivar str message: Short message of what went wrong.
    :ivar str description: Longer description of what went wrong.
    """

    def __init__(self, code, message, description):
        """Initializes the exception.

        :param int code: Error code.
        :param str message: Short message describing what went wrong.
        :param str description: Longer description of what went wrong.
        """
        super().__init__(description)

        self.code = code
        self.message = message
        self.description = description
