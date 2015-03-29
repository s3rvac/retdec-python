#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.fileinfo` module."""

from unittest import mock

from tests.resource_tests import WithMockedIO
from retdec.exceptions import AnalysisFailedError
from retdec.file import File
from retdec.fileinfo import Analysis
from retdec.fileinfo import Fileinfo
from tests.file_tests import AnyFile
from tests.resource_tests import ResourceTestsBase
from tests.resource_tests import WithDisabledWaitingInterval
from tests.service_tests import BaseServiceTests


class FileinfoTests(BaseServiceTests):
    """Tests for :class:`retdec.fileinfo.Fileinfo`."""

    def test_repr_returns_correct_value(self):
        fileinfo = Fileinfo(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )
        self.assertEqual(
            repr(fileinfo),
            "<retdec.fileinfo.Fileinfo api_url='https://retdec.com/service/api'>"
        )


class FileinfoRunAnalysisTests(BaseServiceTests):
    """Tests for :func:`retdec.fileinfo.Fileinfo.run_analysis()`."""

    def setUp(self):
        super().setUp()

        self.input_file = mock.MagicMock(spec_set=File)

        self.fileinfo = Fileinfo(api_key='KEY')

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.fileinfo.run_analysis(input_file=self.input_file)

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/fileinfo/analyses',
            self.fileinfo.api_key
        )

    def test_verbose_is_set_to_0_when_not_given(self):
        self.fileinfo.run_analysis(input_file=self.input_file)

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={'verbose': 0},
            files={'input': AnyFile()}
        )

    def test_verbose_is_set_to_0_when_given_but_false(self):
        self.fileinfo.run_analysis(
            input_file=self.input_file,
            verbose=False
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={'verbose': 0},
            files={'input': AnyFile()}
        )

    def test_verbose_is_set_to_1_when_given_and_true(self):
        self.fileinfo.run_analysis(
            input_file=self.input_file,
            verbose=True
        )

        self.conn.send_post_request.assert_called_once_with(
            '',
            params={'verbose': 1},
            files={'input': AnyFile()}
        )

    def test_uses_returned_id_to_initialize_analysis(self):
        self.conn.send_post_request.return_value = {'id': 'ID'}

        analysis = self.fileinfo.run_analysis(
            input_file=self.input_file
        )

        self.assertTrue(analysis.id, 'ID')


class AnalysisTestsBase(ResourceTestsBase):
    """Base class of all tests of :class:`retdec.decompiler.Analysis`."""


class AnalysisTests(AnalysisTestsBase):
    """Tests for :class:`retdec.fileinfo.Analysis`."""

    def test_repr_returns_correct_value(self):
        a = Analysis('ID', self.conn)
        self.assertEqual(
            repr(a),
            "<retdec.fileinfo.Analysis id='ID'>"
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

        self.conn.send_get_request.assert_called_once_with('/ID/status')

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
    :class:`retdec.fileinfo.Analysis`.
    """

    def test_get_output_obtains_file_contents(self):
        a = Analysis('ID', self.conn)
        self.assert_obtains_file_contents(
            a.get_output,
            '/ID/output',
            is_text_file=True
        )
