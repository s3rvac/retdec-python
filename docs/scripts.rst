.. title:: Scripts

Scripts
=======

This page describes the `retdec-python <https://github.com/s3rvac/retdec-python>`_ scripts and their usage.

Currently, there are two scripts: ``decompiler`` and ``fileinfo``. They provide access to the `decompilation <https://retdec.com/api/docs/decompiler.html>`_ and `file-analyzing <https://retdec.com/api/docs/fileinfo.html>`_ services, respectively.

Authentication
--------------

The scripts need to authenticate you to `retdec.com <https://retdec.com>`_. To specify your API key, either use the ``-k KEY`` or ``--api-key KEY`` parameter:

.. code::

    $ decompiler -k YOUR-API-KEY file.exe

or set the ``RETDEC_API_KEY`` environment variable:

.. code::

    $ export RETDEC_API_KEY=YOUR-API-KEY
    $ decompiler file.exe

An advantage of the environment variable is that you do not have to specify the API key every time you run a script.

.. _decompiler:

Decompiler
----------

The ``decompiler`` script provides access to the `decompilation service <https://retdec.com/api/docs/decompiler.html>`_. It allows you to decompile binary files into a high-level language representation, such as C.

Usage
^^^^^
.. code::

    $ decompiler [OPTIONS] FILE

Output files are stored into the same directory where the input file is located. For example, if the input file is ``dir/prog.exe``, then the decompiled code in the C language is saved as ``dir/prog.c``. You can override the output directory by using the ``-o/--output-dir`` parameter.

* ``-k KEY, --api-key KEY`` -- Specifies the API key to be used.
* ``-b, --brief`` -- Prints fewer information during the decompilation.
* ``-m MODE, --mode MODE`` -- Decompilation mode. `Supported modes <https://retdec.com/api/docs/decompiler.html#decompilation-modes>`_: ``bin``, ``c``. By default, the script performs an automatic detection based on the file's extension.
* ``-o DIR, --output-dir DIR`` -- Saves the outputs into this directory.
* ``-q, --quiet`` -- Prints only errors, nothing else (not even progress).
* ``--with-archive`` -- Generates an archive containing all decompilation outputs. At the moment, the archive contains only the C source code and disassembled code.

Example
^^^^^^^

.. code::

    $ decompiler -k YOUR-API-KEY file.exe

    v23bmYb67R
    ----------

    Waiting for resources (0%)...                      [OK]
    Pre-Processing:
        Obtaining file information (5%)...             [OK]
        Unpacking (10%)...                             [OK]
    Front-End:
        Initializing (20%)...                          [OK]
    [..]
    Done (100%)...

    Downloading:
     - file.c

``file.c`` then contains the decompiled C code.

.. _fileinfo:

Fileinfo
--------

The ``fileinfo`` script provides access to the `file-analyzing service <https://retdec.com/api/docs/fileinfo.html>`_. It allows you to obtain information about binary files.

Usage
^^^^^
.. code::

    $ fileinfo [OPTIONS] FILE

Options
^^^^^^^

* ``-k KEY, --api-key KEY`` -- Specifies the API key to be used.
* ``-v, --verbose`` -- Print all available information about the file.

Example
^^^^^^^

.. code::

    $ fileinfo -k YOUR-API-KEY file.exe

    Input file               : file.exe
    File format              : PE
    File class               : 32-bit
    File type                : Executable file
    Architecture             : x86 (or later and compatible)
    Endianness               : Little endian
    Entry point address      : 0x4014e0
    Entry point offset       : 0x8e0
    Entry point section name : .text
    Entry point section index: 0
    Bytes on entry point     : 31ed5e89e183e4f05054526860c1040868f0c00408515668babd0408e8bffffffff466906690669066906690669066908b1c
    Detected compiler/packer : GCC (x86_64-unknown-linux-gnu) (4.7.2) (100%) (51 from 51 significant nibbles)
