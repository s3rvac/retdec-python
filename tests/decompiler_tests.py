#
# Project:   retdec-python
# Copyright: (c) 2015-2016 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#

"""Tests for the :mod:`retdec.decompiler` module."""

from retdec.decompiler import Decompiler
from retdec.exceptions import InvalidValueError
from retdec.exceptions import MissingParameterError
from retdec.file import File
from tests import mock
from tests.conn_tests import AnyFilesWith
from tests.conn_tests import AnyParamsWith
from tests.file_tests import AnyFileNamed
from tests.service_tests import BaseServiceTests


class DecompilerTests(BaseServiceTests):
    """Tests for :class:`retdec.decompiler.Decompiler`."""

    def test_repr_returns_correct_value(self):
        decompiler = Decompiler(
            api_key='API-KEY',
            api_url='https://retdec.com/service/api/'
        )

        self.assertEqual(
            repr(decompiler),
            "<retdec.decompiler.Decompiler api_url='https://retdec.com/service/api'>"
        )


class DecompilerStartDecompilationTests(BaseServiceTests):
    """Tests for :func:`retdec.decompiler.Decompiler.start_decompilation()`."""

    def setUp(self):
        super().setUp()

        self.input_file = mock.Mock(spec_set=File)

        self.decompiler = Decompiler(api_key='KEY')

    def start_decompilation(self, *args, **kwargs):
        """Starts a decompilation with the given parameters."""
        return self.decompiler.start_decompilation(*args, **kwargs)

    def start_decompilation_with_any_input_file(self, *args, **kwargs):
        """Starts a decompilation with the default input file and,
        additionally, the given parameters.
        """
        kwargs.setdefault('input_file', self.input_file)
        return self.decompiler.start_decompilation(*args, **kwargs)

    def test_creates_api_connection_with_correct_url_and_api_key(self):
        self.start_decompilation_with_any_input_file()

        self.APIConnectionMock.assert_called_once_with(
            'https://retdec.com/service/api/decompiler/decompilations',
            self.decompiler.api_key
        )

    def test_sends_input_file(self):
        self.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            files=AnyFilesWith(input=AnyFileNamed(self.input_file.name))
        )

    def test_raises_exception_when_input_file_is_not_given(self):
        with self.assertRaises(MissingParameterError):
            self.start_decompilation()

    def test_sends_pdb_file_when_given(self):
        pdb_file = mock.Mock(spec_set=File)

        self.start_decompilation_with_any_input_file(
            pdb_file=pdb_file
        )

        self.assert_post_request_was_sent_with(
            files=AnyFilesWith(pdb=AnyFileNamed(pdb_file.name))
        )

    def test_mode_is_set_to_c_when_not_given_and_file_name_ends_with_c(self):
        self.input_file.name = 'test.c'

        self.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='c')
        )

    def test_mode_is_set_to_bin_when_not_given_and_file_name_does_not_end_with_c(self):
        self.input_file.name = 'test.exe'

        self.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='bin')
        )

    def test_mode_is_used_when_given(self):
        self.start_decompilation_with_any_input_file(
            mode='bin'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='bin')
        )

    def test_raises_exception_when_mode_is_invalid(self):
        with self.assertRaises(InvalidValueError):
            self.start_decompilation_with_any_input_file(
                mode='xxx'
            )

    def test_file_name_extension_is_case_insensitive_during_mode_detection(self):
        self.input_file.name = 'test.C'

        self.start_decompilation(input_file=self.input_file)

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(mode='c')
        )

    def test_target_language_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            target_language='py'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(target_language='py')
        )

    def test_graph_format_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            graph_format='svg'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(graph_format='svg')
        )

    def test_decomp_var_names_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            decomp_var_names='simple'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(decomp_var_names='simple')
        )

    def test_decomp_optimizations_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            decomp_optimizations='none'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(decomp_optimizations='none')
        )

    def test_decomp_unreach_funcs_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            decomp_unreach_funcs=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(decomp_unreach_funcs=True)
        )

    def test_decomp_emit_addresses_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            decomp_emit_addresses=False
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(decomp_emit_addresses=False)
        )

    def test_architecture_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            architecture='arm'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(architecture='arm')
        )

    def test_file_format_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            file_format='elf'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(file_format='elf')
        )

    def test_comp_compiler_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            comp_compiler='clang'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(comp_compiler='clang')
        )

    def test_comp_optimizations_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            comp_optimizations='-O1'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(comp_optimizations='-O1')
        )

    def test_comp_debug_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            comp_debug=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(comp_debug=True)
        )

    def test_comp_strip_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            comp_strip=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(comp_strip=True)
        )

    def test_adds_leading_dash_to_comp_optimizations_when_missing(self):
        self.start_decompilation_with_any_input_file(
            comp_optimizations='O1'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(comp_optimizations='-O1')
        )

    def test_sel_decomp_funcs_is_passed_directly_when_given_as_str(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_funcs='func1,func2'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_funcs='func1,func2')
        )

    def test_sel_decomp_funcs_is_converted_to_str_when_given_as_list(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_funcs=['func1', 'func2']
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_funcs='func1,func2')
        )

    def test_sel_decomp_ranges_is_passed_directly_when_given_as_str(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_ranges='0x100-0x200,0x400-0x500'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_ranges='0x100-0x200,0x400-0x500')
        )

    def test_sel_decomp_ranges_is_converted_to_str_when_given_as_list_with_str(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_ranges=['0x100-0x200', '0x400-0x500']
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_ranges='0x100-0x200,0x400-0x500')
        )

    def test_sel_decomp_ranges_is_converted_to_str_when_given_as_list_with_int_tuples(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_ranges=[(0x100, 0x200), (0x400, 0x500)]
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_ranges='0x100-0x200,0x400-0x500')
        )

    def test_sel_decomp_ranges_is_converted_to_str_when_given_as_list_with_str_tuples(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_ranges=[('0x100', '0x200'), ('0x400', '0x500')]
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_ranges='0x100-0x200,0x400-0x500')
        )

    def test_asserts_when_invalid_range_is_passed(self):
        with self.assertRaisesRegex(AssertionError, r'invalid range'):
            self.start_decompilation_with_any_input_file(
                sel_decomp_ranges=[(0x100,)]
            )

    def test_sel_decomp_decoding_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            sel_decomp_decoding='only'
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(sel_decomp_decoding='only')
        )

    def test_generate_cg_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            generate_cg=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_cg=True)
        )

    def test_generate_cfgs_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            generate_cfgs=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_cfgs=True)
        )

    def test_generate_archive_is_set_to_correct_value_when_given(self):
        self.start_decompilation_with_any_input_file(
            generate_archive=True
        )

        self.assert_post_request_was_sent_with(
            params=AnyParamsWith(generate_archive=True)
        )

    def test_uses_returned_id_to_initialize_decompilation(self):
        self.conn.send_post_request.return_value = {'id': 'ID'}

        decompilation = self.start_decompilation_with_any_input_file()

        self.assertTrue(decompilation.id, 'ID')
