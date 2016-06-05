#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Representation of a file."""


class File:
    """Representation of a file.

    :param str/file-like object file: Either path to the file (`str`) or an
        opened file (a file-like object).
    :param str name: Name of the file to be used.

    When `name` is not given or it is ``None``, the name is taken from `file`.
    You can use `name` to set a custom file name that may be different from the
    real file's name.
    """

    def __init__(self, file, name=None):
        if isinstance(file, str):
            # We got a path to the file. Since we do not know whether the file
            # is a binary or text file, open it in the binary mode to ensure
            # that no conversions are done during reading.
            file = open(file, 'rb')

        self._file = file
        self._name = name

    @property
    def name(self):
        """Name of the file (`str`).

        May be ``None`` if the file has no name.
        """
        if self._name is not None:
            return self._name
        return getattr(self._file, 'name', None)

    @property
    def mode(self):
        """Mode in which the file is opened.

        If the file does not have a mode, it returns ``None``.
        """
        return getattr(self._file, 'mode', None)

    def __repr__(self):
        return "<{} name={!r} mode={!r}>".format(
            __name__ + '.' + self.__class__.__name__,
            self.name,
            self.mode
        )

    # Delegate other attributes to the underlying file.

    def __getattr__(self, attr):
        return getattr(self._file, attr)
