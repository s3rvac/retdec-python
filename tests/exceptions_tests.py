#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.exceptions` module."""

import unittest

from retdec.exceptions import AnalysisFailedError
from retdec.exceptions import ArchiveGenerationFailedError
from retdec.exceptions import AuthenticationError
from retdec.exceptions import ConnectionError
from retdec.exceptions import DecompilationFailedError
from retdec.exceptions import InvalidValueError
from retdec.exceptions import MissingAPIKeyError
from retdec.exceptions import MissingParameterError
from retdec.exceptions import OutputNotRequestedError
from retdec.exceptions import UnknownAPIError


class MissingAPIKeyErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.MissingAPIKeyError`."""

    def test_has_correct_description(self):
        ex = MissingAPIKeyError()
        self.assertIn('API key', str(ex))
        self.assertIn('RETDEC_API_KEY', str(ex))


class MissingParameterErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.MissingAPIKeyError`."""

    def test_has_correct_description(self):
        ex = MissingParameterError('PARAM_NAME')
        self.assertIn('PARAM_NAME', str(ex))


class InvalidValueErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.MissingAPIKeyError`."""

    def test_has_correct_description(self):
        ex = InvalidValueError('PARAM_NAME', 'PARAM_VALUE')
        self.assertIn('PARAM_NAME', str(ex))
        self.assertIn('PARAM_VALUE', str(ex))


class AuthenticationErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.AuthenticationError`."""

    def test_has_correct_description(self):
        ex = AuthenticationError()
        self.assertIn('API key', str(ex))
        self.assertIn('failed', str(ex))


class ConnectionErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.ConnectionError`."""

    def test_does_not_include_reason_when_not_given(self):
        ex = ConnectionError()
        self.assertNotIn('reason', str(ex))

    def test_includes_reason_when_given(self):
        ex = ConnectionError('REASON')
        self.assertIn('REASON', str(ex))


class AnalysisFailedErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.AnalysisFailedError`."""

    def test_does_not_include_reason_when_not_given(self):
        ex = AnalysisFailedError()
        self.assertNotIn('reason', str(ex))

    def test_includes_reason_when_given(self):
        ex = AnalysisFailedError('REASON')
        self.assertIn('REASON', str(ex))


class DecompilationFailedErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.DecompilationFailedError`."""

    def test_does_not_include_reason_when_not_given(self):
        ex = DecompilationFailedError()
        self.assertNotIn('reason', str(ex))

    def test_includes_reason_when_given(self):
        ex = DecompilationFailedError('REASON')
        self.assertIn('REASON', str(ex))


class OutputNotRequestedErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.OutputNotRequestedError`."""

    def test_has_correct_description(self):
        ex = OutputNotRequestedError()
        self.assertIn('not requested', str(ex))


class ArchiveGenerationFailedErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.ArchiveGenerationFailedError`."""

    def test_does_not_include_reason_when_not_given(self):
        ex = ArchiveGenerationFailedError()
        self.assertNotIn('reason', str(ex))

    def test_includes_reason_when_given(self):
        ex = ArchiveGenerationFailedError('REASON')
        self.assertIn('REASON', str(ex))


class UnknownAPIErrorTests(unittest.TestCase):
    """Tests for :class:`retdec.exceptions.UnknownAPIError`."""

    def test_has_correct_attributes(self):
        ex = UnknownAPIError(401, 'message', 'description')
        self.assertEqual(ex.code, 401)
        self.assertEqual(ex.message, 'message')
        self.assertEqual(ex.description, 'description')

    def test_str_gives_description(self):
        ex = UnknownAPIError(401, 'message', 'description')
        self.assertEqual(str(ex), 'description')
