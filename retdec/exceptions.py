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


class APIError(RetdecError):
    """Base class of exceptions reflecting errors reported by the API.

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


class AuthenticationError(APIError):
    """Exception raised when authentication with the provided API key fails."""
