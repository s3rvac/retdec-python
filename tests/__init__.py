#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the library and tools."""

import abc
from unittest import mock


# Do not inherit from unittest.TestCase because WithPatching is a mixin, not a
# base class for tests.
class WithPatching:
    """Mixin for tests that perform patching during their setup."""

    def patch(self, what, with_what):
        """Patches `what` with `with_what`."""
        patcher = mock.patch(what, with_what)
        patcher.start()
        self.addCleanup(patcher.stop)


class Matcher(metaclass=abc.ABCMeta):
    """A base class of all matchers."""

    @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        name = self.__class__.__qualname__
        attr_list = ', '.join(
            '{}={!r}'.format(key, value) for key, value in self.__dict__.items()
        )
        return '{}({})'.format(name, attr_list)


class Anything(Matcher):
    """A matcher that matches anything."""

    def __eq__(self, other):
        return True


class AnyDictWith(Matcher):
    """A matcher that matches and ``dict`` with the given keys and values.

    The ``dict`` may also have other keys and values, which are not considered
    during the matching.
    """

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __eq__(self, other):
        if not isinstance(other, dict):
            return False
        for name, value in self.__dict__.items():
            if name not in other or other[name] != value:
                return False
        return True
