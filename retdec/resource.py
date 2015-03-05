#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Base class of all resources."""

import datetime
import time


class Resource:
    """Base class of all resources."""

    #: Time interval after which we can update resource's state.
    _STATE_UPDATE_INTERVAL = datetime.timedelta(seconds=0.5)

    def __init__(self, id, conn):
        """Initializes the resource.

        :param str id: Unique identifier of the resource.
        :param retdec.conn.APIConnection conn: Connection to the API to be used
                                               for sending API requests.
        """
        self._id = id
        self._conn = conn

        # To prevent abuse of the API, we update the state of the resource only
        # once in a while. In order to track whether we should perform an
        # update, we keep a date and time of the last update. By initializing
        # it to the minimal representable date, we ensure that the resource
        # gets updated upon the first call of a state-checking method, like
        # has_finished().
        # See the implementation of _state_should_be_updated() for more details.
        self._last_updated = datetime.datetime.min

    @property
    def id(self):
        """Unique identifier of the resource."""
        return self._id

    def is_pending(self):
        """Is the resource in a pending state?

        A resource is *pending* if it is scheduled to run but has not started
        yet.
        """
        self._update_state_if_needed()
        return self._pending

    def is_running(self):
        """Is the resource currently running?"""
        self._update_state_if_needed()
        return self._running

    def has_finished(self):
        """Has the resource finished?"""
        self._update_state_if_needed()
        return self._finished

    def has_succeeded(self):
        """Has the resource succeeded?"""
        self._update_state_if_needed()
        return self._finished

    def has_failed(self):
        """Has the resource failed?

        For finished resources, this is always the negation of
        :func:`has_succeeded()`.
        """
        self._update_state_if_needed()
        return self._failed

    def get_error(self):
        """A reason why the resource failed.

        If the resource has not failed, it returns ``None``.
        """
        self._update_state_if_needed()
        return self._error

    def _update_state_if_needed(self):
        """Updates the state of the resource (if needed)."""
        if self._state_should_be_updated():
            self._update_state()

    def _state_should_be_updated(self):
        """Should the state of the resource be updated?"""
        # To prevent abuse of the API, update the status only once in a while.
        now = datetime.datetime.now()
        return (now - self._last_updated) > self._STATE_UPDATE_INTERVAL

    def _wait_until_state_can_be_updated(self):
        """Waits until the state can be updated."""
        time.sleep(self._STATE_UPDATE_INTERVAL.total_seconds())

    def _update_state(self):
        """Updates the state of the resource."""
        status = self._get_status()
        self._pending = status['pending']
        self._running = status['running']
        self._finished = status['finished']
        self._succeeded = status['succeeded']
        self._failed = status['failed']
        self._error = status['error']
        self._last_updated = datetime.datetime.now()
        return status

    def _get_status(self):
        """Obtains and returns the current status of the resource."""
        return self._conn.send_get_request('/{}/status'.format(self.id))
