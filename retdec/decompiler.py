#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Access to the decompiler (decompilation of files)."""

from retdec.decompilation import Decompilation
from retdec.exceptions import MissingParameterError
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
        :param target_language: Target high-level language.
        :type target_language: str
        :param architecture: Architecture. The precise meaning depends on the
            used `mode`.
        :type architecture: str
        :param file_format: File format. The precise meaning depends on the
            used `mode`.
        :type file_format: str
        :param comp_compiler: Compiler to be used when compiling input C source
            files.
        :type comp_compiler: str
        :param comp_optimizations: Compiler optimizations to be used when
            compiling input C source files.
        :type comp_optimizations: str
        :param comp_debug: Should the input C source file be compiled with
            debugging information?
        :type comp_debug: bool
        :param comp_strip: Should the compiled input C source file be stripped?
        :type comp_strip: bool
        :param generate_archive: Should an archive containing all outputs from
            the decompilation be generated?
        :type generate_archive: bool

        :returns: Started decompilation
            (:class:`~retdec.decompilation.Decompilation`).

        If `mode` is not given, it is automatically determined based on the
        name of ``input_file``. If the input file ends with ``.c`` or ``.C``,
        the mode is set to ``c``. Otherwise, the mode is set to ``bin``.

        See the `official documentation
        <https://retdec.com/api/docs/decompiler.html#decompilation-parameters>`_
        for more information about the parameters.
        """
        conn = self._create_new_api_connection('/decompiler/decompilations')
        id = self._start_decompilation(conn, kwargs)
        return Decompilation(id, conn)

    def _start_decompilation(self, conn, kwargs):
        """Starts a decompilation with the given parameters.

        :param retdec.conn.APIConnection conn: Connection to the API to be used
            for sending API requests.
        :param dict kwargs: Parameters for the decompilation.

        :returns: Unique identifier of the decompilation.
        """
        files = {
            'input': self._get_input_file(kwargs)
        }
        self._add_pdb_file_when_given(files, kwargs)
        params = {
            'mode': self._get_mode_param(files['input'], kwargs)
        }
        self._add_param_when_given('target_language', params, kwargs)
        self._add_param_when_given('architecture', params, kwargs)
        self._add_param_when_given('file_format', params, kwargs)
        self._add_param_when_given('comp_compiler', params, kwargs)
        self._add_param_when_given('comp_debug', params, kwargs)
        self._add_param_when_given('comp_strip', params, kwargs)
        self._add_comp_optimizations_param_when_given(params, kwargs)
        self._add_param_when_given('generate_archive', params, kwargs)
        response = conn.send_post_request(files=files, params=params)
        return response['id']

    def _get_input_file(self, kwargs):
        """Returns the input file to be decompiled."""
        try:
            return File(kwargs['input_file'])
        except KeyError:
            raise MissingParameterError('input_file')

    def _add_pdb_file_when_given(self, files, kwargs):
        """Adds a PDB file to `files` when it was given."""
        pdb_file = kwargs.get('pdb_file', None)
        if pdb_file is not None:
            files['pdb'] = File(pdb_file)

    def _get_mode_param(self, input_file, kwargs):
        """Returns a decompilation mode to be used."""
        return self._get_param(
            'mode',
            kwargs,
            choices={'c', 'bin'},
            default=self._get_default_mode(input_file)
        )

    def _get_default_mode(self, input_file):
        """Returns a default decompilation mode to be used based on the given
        input file's name.
        """
        return 'c' if input_file.name.lower().endswith('.c') else 'bin'

    def _add_param_when_given(self, param, params, kwargs):
        """Adds `param` to `params` when given in `kwargs`."""
        value = kwargs.get(param, None)
        if value is not None:
            params[param] = value

    def _add_comp_optimizations_param_when_given(self, params, kwargs):
        """Adds the ``comp_optimizations`` parameter to `params` when given in
        `kwargs`.
        """
        value = kwargs.get('comp_optimizations', None)
        if value is not None:
            # The retdec.com API expects the optimization level to start with a
            # dash (e.g. "-O1" instead of just "O1"). To be user-friendly,
            # allow passing just "O1" and add the dash automatically.
            if not value.startswith('-'):
                value = '-' + value
            params['comp_optimizations'] = value

    def __repr__(self):
        return '<{} api_url={!r}>'.format(
            __name__ + '.' + self.__class__.__name__,
            self.api_url
        )
