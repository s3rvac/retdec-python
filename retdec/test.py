#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the testing service."""

from retdec.service import Service


class Test(Service):
    """Access to the testing service."""

    def auth(self):
        """Tries to authenticate.

        :raises ``AuthenticationError``: When the authentication fails.

        Does nothing when the authentication succeeds.
        """
        conn = self._create_new_api_connection('/test/echo')
        # We do not need any parameters; simply send a GET request to
        # /test/echo, and if authentication fails, send_get_request() raises
        # AuthenticationError.
        conn.send_get_request()
