#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the library and tools."""

import abc


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
            '{}={!r}'.format(name, value) for name, value in self.__dict__.items()
        )
        return '{}({})'.format(name, attr_list)
