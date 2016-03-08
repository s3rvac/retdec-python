#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Phase of a decompilation."""


class DecompilationPhase:
    """Phase of a decompilation."""

    def __init__(self, name, part, description, completion):
        """
        :param str name: Name of the phase.
        :param str part: Part into which the phase belongs.
        :param str description: Description of the phase.
        :param int completion: What percentage of the decompilation has been
                               completed?

        `part` may be ``None`` if the phase does not belong to any part.
        """
        self._name = name
        self._part = part
        self._description = description
        self._completion = completion

    @property
    def name(self):
        """Name of the phase (`str`)."""
        return self._name

    @property
    def part(self):
        """Part to which the phase belongs (`str`).

        May be ``None`` if the phase does not belong to any part.
        """
        return self._part

    @property
    def description(self):
        """Description of the phase (`str`)."""
        return self._description

    @property
    def completion(self):
        """Completion (in percentages, ``0-100``)."""
        return self._completion

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '{}(name={!r}, part={!r}, description={!r}, completion={})'.format(
            __name__ + '.' + self.__class__.__name__,
            self.name,
            self.part,
            self.description,
            self.completion
        )
