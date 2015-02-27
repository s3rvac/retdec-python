#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Base class of all resources."""

import time


class Resource:
    """Base class of all resources."""

    def __init__(self, id, conn):
        """Initializes the resource.

        :param str id: Unique identifier of the resource.
        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.
        """
        self._id = id
        self._conn = conn

    @property
    def id(self):
        """Unique identifier of the resource."""
        return self._id

    def wait_until_finished(self):
        """Waits until the resource is finished."""
        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        while True:
            response = self._conn.send_get_request('/{}/status'.format(self.id))
            if response['finished']:
                break
            # Sleep a bit to prevent abuse of the API.
            time.sleep(0.5)
