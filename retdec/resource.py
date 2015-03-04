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

    def wait_until_finished(self, callback=None,
                            on_failure=ResourceFailedError):
        """Waits until the resource is finished.

        :param callable callback: Function to be called when the status of the
                                  resource is changed or it finishes.
        :param callable on_failure: What should be done when the resource
                                    fails?

        If `callback` is not ``None``, it is called with the resource as its
        argument when the status of the resource is changed or when it
        finishes.

        If `on_failure` is ``None``, nothing is done when the resource fails.
        Otherwise, it is called with the error message. If the returned value
        is an exception, it is raised.
        """
        # Ensure that we have something callable (do nothing by default).
        callback = callback or (lambda _: None)

        # Currently, the retdec.com API does not support push notifications, so
        # we have to do polling.
        # Track completion changes so we can call the callback when the status
        # changes.
        last_completion = None
        while True:
            status = self._get_status()

            if status['finished']:
                break

            if (last_completion is not None and
                    status['completion'] != last_completion):
                callback(self)
            last_completion = status['completion']

            # Sleep a bit to prevent abuse of the API.
            time.sleep(0.5)

        # The resource has finished.

        # Call the callback one final time. This has to be done because the
        # resource may have immediately finished, without giving us chance to
        # call the callback.
        callback(self)

        if status['failed'] and on_failure is not None:
            obj = on_failure(status['error'])
            if isinstance(obj, Exception):
                raise obj

    def _get_status(self):
        """Returns the current status of the resource."""
        return self._conn.send_get_request('/{}/status'.format(self.id))
