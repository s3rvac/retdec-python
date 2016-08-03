.. title:: Status

Status
======

A summary of the supported parts of the `retdec.com API <https://retdec.com/api/docs/index.html>`_.

Decompiler
----------

The decompilation service.

* `Starting a new decompilation <https://retdec.com/api/docs/decompiler.html#starting-a-new-decompilation>`_ ✔
* `Decompilation modes <https://retdec.com/api/docs/decompiler.html#decompilation-modes>`_ ✔

    * ``bin`` ✔
    * ``c`` ✔
    * ``raw`` ✔

* `Input files <https://retdec.com/api/docs/decompiler.html#input-files>`_ ✔

    * ``input`` ✔
    * ``pdb`` ✔

* `Decompilation parameters <https://retdec.com/api/docs/decompiler.html#decompilation-parameters>`_ ✔

    * `Mode-independent parameters <https://retdec.com/api/docs/decompiler.html#mode-independent-parameters>`_ ✔

        * ``target_language`` ✔
        * ``graph_format`` ✔
        * ``decomp_var_names`` ✔
        * ``decomp_optimizations`` ✔
        * ``decomp_unreach_funcs`` ✔
        * ``decomp_emit_addresses`` ✔
        * ``generate_cg`` ✔
        * ``generate_cfgs`` ✔
        * ``generate_archive`` ✔

    * `Parameters for the bin mode <https://retdec.com/api/docs/decompiler.html#parameters-only-for-the-bin-mode>`_ ✔

        * ``architecture`` ✔
        * ``sel_decomp_funcs`` ✔
        * ``sel_decomp_ranges`` ✔
        * ``sel_decomp_decoding`` ✔

    * `Parameters for the raw mode <https://retdec.com/api/docs/decompiler.html#parameters-only-for-the-raw-mode>`_ ✔

        * ``architecture`` ✔
        * ``file_format`` ✔
        * ``raw_endian`` ✔
        * ``raw_entry_point`` ✔
        * ``raw_section_vma`` ✔

    * `Parameters for the c mode <https://retdec.com/api/docs/decompiler.html#parameters-only-for-the-c-mode>`_ ✔

        * ``architecture`` ✔
        * ``file_format`` ✔
        * ``comp_compiler`` ✔
        * ``comp_optimizations`` ✔
        * ``comp_debug`` ✔
        * ``comp_strip`` ✔

* `Checking status <https://retdec.com/api/docs/decompiler.html#checking-status>`__ ✔

    * general (``running``, ``finished``, etc.) ✔
    * ``completion`` ✔
    * ``phases`` ✔

        * ``part`` ✔
        * ``name`` ✔
        * ``description`` ✔
        * ``completion`` ✔
        * ``warnings`` ✔

    * ``cg`` ✔
    * ``cfgs`` ✔
    * ``archive`` ✔

* `Obtaining outputs <https://retdec.com/api/docs/decompiler.html#obtaining-outputs>`_ ✔

    * ``hll`` ✔
    * ``dsm`` ✔
    * ``cg`` ✔
    * ``cfgs`` ✔
    * ``archive`` ✔
    * ``binary`` ✔

* `Error reporting <https://retdec.com/api/docs/decompiler.html#error-reporting>`__ ✔

Fileinfo
--------

The file-analyzing service.

* `Starting a new analysis <https://retdec.com/api/docs/fileinfo.html#starting-a-new-analysis>`_ ✔
* `Optional parameters <https://retdec.com/api/docs/fileinfo.html#optional-parameters>`_ ✔

    * ``verbose`` ✔

* `Checking status <https://retdec.com/api/docs/fileinfo.html#checking-status>`__ ✔

    * general (``running``, ``finished``, etc.) ✔

* `Obtaining output <https://retdec.com/api/docs/fileinfo.html#obtaining-output>`_ ✔
* `Error reporting <https://retdec.com/api/docs/fileinfo.html#error-reporting>`__ ✔

Test
----

The testing service.

* `Authentication <https://retdec.com/api/docs/test.html#authentication>`_ ✔
* `Parameter passing <https://retdec.com/api/docs/test.html#parameter-passing>`_ ✔
