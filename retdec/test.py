"""
    Access to the testing service.

    :copyright: © 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
    :license: MIT, see the ``LICENSE`` file for more details
"""

from retdec.service import Service


class Test(Service):
    """Access to the testing service."""

    def auth(self):
        """Tries authentication.

        :raises ``AuthenticationError``: When the authentication fails.
        """
        conn = self._create_new_api_connection('/test/echo')
        # We do not need any parameters; simply send a GET request to
        # /test/echo, and if authentication fails, send_get_request() raises
        # AuthenticationError.
        conn.send_get_request()
