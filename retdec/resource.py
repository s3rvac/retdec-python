#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Base class of all resources."""

import time

from retdec.exceptions import ResourceFailedError


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

    def wait_until_finished(self, on_failure=ResourceFailedError):
        """Waits until the resource is finished.

        :param callable on_failure: What should be done when the resource
                                    fails?

        If `on_failure` is ``None``, nothing is done when the resource fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        def get_status():
            return self._conn.send_get_request('/{}/status'.format(self.id))

        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        status = get_status()
        while not status['finished']:
            # Sleep a bit to prevent abuse of the API.
            time.sleep(0.5)

            # Try it again.
            status = get_status()

        # The resource has finished.
        if status['failed'] and on_failure is not None:
            obj = on_failure(status['error'])
            if isinstance(obj, Exception):
                raise obj
