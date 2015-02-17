"""
    retdec.exceptions
    ~~~~~~~~~~~~~~~~~

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
