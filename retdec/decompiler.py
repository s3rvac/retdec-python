#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the decompiler (decompilation of files)."""

from retdec.decompilation import Decompilation
from retdec.file import File
from retdec.service import Service


class Decompiler(Service):
    """Access to the decompilation service."""

    def start_decompilation(self, **kwargs):
        """Starts a decompilation with the given parameters.

        :param input_file: File to be analyzed (**required**).
        :type input_file: str or file-like object
        :param pdb_file: A PDB file associated with `input_file` containing
            debugging information.
        :type pdb_file: str or file-like object
        :param mode: Decompilation mode.
        :type mode: str
        :param generate_archive: Should an archive containing all outputs from
            the decompilation be generated? ``False`` by default.
        :type generate_archive: bool

        :returns: Started decompilation
            (:class:`~retdec.decompilation.Decompilation`).

        If `mode` is not given, it is automatically determined based on the
        name of ``input_file``. If the input file ends with ``.c`` or ``.C``,
        the mode is set to ``c``. Otherwise, the mode is set to ``bin``.
        """
        conn = self._create_new_api_connection('/decompiler/decompilations')
        id = self._start_decompilation(conn, **kwargs)
        return Decompilation(id, conn)

    def _start_decompilation(self, conn, **kwargs):
        """Starts a decompilation with the given parameters.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
            for sending API requests.

        :returns: Unique identifier of the decompilation.
        """
        # The input file is always required.
        input_file = self._get_input_file(kwargs)

        params = {
            'mode': self._get_mode_param(input_file, kwargs),
            'generate_archive': self._get_generate_archive_param(kwargs)
        }
        files = {
            'input': input_file
        }
        self._add_pdb_file_when_given(files, kwargs)
        response = conn.send_post_request('', params=params, files=files)
        return response['id']

    def _get_mode_param(self, input_file, params):
        """Returns a mode from the given parameters (``dict``)."""
        return self._get_param(
            'mode',
            params,
            choices={'c', 'bin'},
            default=self._get_default_mode(input_file)
        )

    def _get_default_mode(self, input_file):
        """Returns a default mode to be used based on the given input file's
        name.
        """
        return 'c' if input_file.name.lower().endswith('.c') else 'bin'

    def _get_input_file(self, params):
        """Returns an input file from the given parameters (``dict``)."""
        if 'input_file' in params:
            return File(params['input_file'])

    def _add_pdb_file_when_given(self, files, params):
        """Adds a PDB file to `files` when given in `params` (``dict``)."""
        pdb_file = params.get('pdb_file', None)
        if pdb_file is not None:
            files['pdb'] = File(pdb_file)

    def _get_generate_archive_param(self, params):
        """Returns whether an archive with all decompilation outputs should be
        generated based on the given parameters (``dict``).
        """
        return self._get_param(
            'generate_archive',
            params,
            choices={True, False},
            default=False
        )

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            __name__ + '.' + self.__class__.__name__,
            self.api_url
        )
