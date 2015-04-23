#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.fileinfo` module."""

from retdec.file import File
from retdec.fileinfo import Fileinfo
from tests import mock
from tests.conn_tests import AnyFilesWith
from tests.conn_tests import AnyParamsWith
from tests.file_tests import AnyFileNamed
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


class FileinfoStartAnalysisTests(BaseServiceTests):
    """Tests for :func:`retdec.fileinfo.Fileinfo.start_analysis()`."""

    def setUp(self):
        super().setUp()

        self.input_file = mock.Mock(spec_set=File)

        self.fileinfo = Fileinfo(api_key='KEY')

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.fileinfo.start_analysis(input_file=self.input_file)

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/fileinfo/analyses',
            self.fileinfo.api_key
        )

    def test_sends_input_file(self):
        self.fileinfo.start_analysis(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            files=AnyFilesWith(input=AnyFileNamed(self.input_file.name))
        )

    def test_verbose_is_set_to_flase_when_not_given(self):
        self.fileinfo.start_analysis(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(verbose=False)
        )

    def test_verbose_is_set_to_False_when_given_but_false(self):
        self.fileinfo.start_analysis(
            input_file=self.input_file,
            verbose=False
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(verbose=False)
        )

    def test_verbose_is_set_to_true_when_given_and_true(self):
        self.fileinfo.start_analysis(
            input_file=self.input_file,
            verbose=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(verbose=True)
        )

    def test_uses_returned_id_to_initialize_analysis(self):
        self.conn.send_post_request.return_value = {'id': 'ID'}

        analysis = self.fileinfo.start_analysis(
            input_file=self.input_file
        )

        self.assertTrue(analysis.id, 'ID')
