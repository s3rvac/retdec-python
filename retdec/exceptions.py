"""
    Custom exceptions raised by the library.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""


class RetdecError(Exception):
    """A base class for all custom exceptions raised by the library."""


class MissingAPIKeyError(RetdecError):
    """Exception raised when an API key is missing."""

    def __init__(self):
        super().__init__(
            'no explicit API key given'
            ' and environment variable RETDEC_API_KEY is not set'
        )


class AuthenticationError(RetdecError):
    """Exception raised when authentication with the provided API key fails."""

    def __init__(self, reason=None):
        if reason is None:
            reason = (
                'failed to authenticate with the provided API key (is it valid?)'
            )
        super().__init__(reason)
