#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.analysis` module."""

from retdec.analysis import Analysis
from retdec.exceptions import AnalysisFailedError
from tests import mock
from tests.resource_tests import ResourceTestsBase
from tests.resource_tests import WithDisabledWaitingInterval
from tests.resource_tests import WithMockedIO


class AnalysisTestsBase(ResourceTestsBase):
    """Base class of all tests of :class:`retdec.decompiler.Analysis`."""


class AnalysisTests(AnalysisTestsBase):
    """Tests for :class:`retdec.analysis.Analysis`."""

    def test_repr_returns_correct_value(self):
        a = Analysis('ID', self.conn)

        self.assertEqual(
            repr(a),
            "<retdec.analysis.Analysis id='ID'>"
        )


# WithDisabledWaitingInterval has to be put as the first base class, see its
# description for the reason why.
class AnalysisWaitUntilFinishedTests(WithDisabledWaitingInterval,
                                     AnalysisTestsBase):
    """Tests for :func:`retdec.resource.Analysis.wait_until_finished()`."""

    def test_sends_correct_request_and_returns_when_resource_is_finished(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True
        })
        a = Analysis('ID', self.conn)

        a.wait_until_finished()

        self.assert_get_request_was_sent_with('/ID/status')

    def test_waits_until_analysis_finishes(self):
        self.conn.send_get_request.side_effect = [
            self.status_with({
                'finished': False,
                'succeeded': False
            }), self.status_with({
                'finished': True,
                'succeeded': True
            })
        ]
        a = Analysis('ID', self.conn)

        a.wait_until_finished()

    def test_raises_exception_by_default_when_resource_failed(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        a = Analysis('ID', self.conn)

        with self.assertRaises(AnalysisFailedError):
            a.wait_until_finished()

    def test_calls_on_failure_when_it_is_callable(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'succeeded': False,
            'failed': True,
            'error': 'error message'
        })
        a = Analysis('ID', self.conn)
        on_failure = mock.Mock()

        a.wait_until_finished(on_failure=on_failure)

        on_failure.assert_called_once_with('error message')

    def test_does_not_raise_exception_when_on_failure_is_none(self):
        self.conn.send_get_request.return_value = self.status_with({
            'finished': True,
            'failed': True,
            'error': 'error message'
        })
        a = Analysis('ID', self.conn)

        a.wait_until_finished(on_failure=None)


# WithMockedIO has to be put as the first base class, see its description for
# the reason why.
class AnalysisGetOutputsTests(WithMockedIO, AnalysisTestsBase):
    """Tests for methods that obtain outputs from an
    :class:`retdec.analysis.Analysis`.
    """

    def test_get_output_obtains_file_contents(self):
        a = Analysis('ID', self.conn)

        self.assert_obtains_file_contents(
            a.get_output,
            '/ID/output',
            is_text_file=True
        )
