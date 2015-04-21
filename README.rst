retdec-python
=============

.. image:: https://readthedocs.org/projects/retdec-python/badge/?version=latest
    :target: https://readthedocs.org/projects/retdec-python/?badge=latest
    :alt: Documentation Status

A Python library and tools providing easy access to the `retdec.com
<https://retdec.com>`_ decompilation service through their public `REST API
<https://retdec.com/api/>`_.

You can either incorporate the library in your own scripts:

.. code-block:: python

    from retdec.decompiler import Decompiler

    decompiler = Decompiler(api_key='YOUR-API-KEY')
    decompilation = decompiler.run_decompilation(input_file='file.exe')
    decompilation.wait_until_finished()
    decompilation.save_hll()

or you can use the built-in scripts for stand-alone decompilations:

.. code-block:: text

    $ python -m retdec.tools.decompiler -k YOUR-API-KEY file.exe
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

Either way, ``file.c`` then contains the decompiled C code.

Development Status
------------------

The library is in an **early stage of development.** It currently provides
basic support of the `decompilation
<https://retdec.com/api/docs/decompiler.html>`_, `fileinfo
<https://retdec.com/api/docs/fileinfo.html>`_, and `test
<https://retdec.com/api/docs/test.html>`_ services.

Dependencies
------------

The library and tools require Python >= 3.3 and the `requests
<http://docs.python-requests.org>`_ module for making HTTPS calls to the
`retdec.com API <https://retdec.com/api/>`_.

Installation
------------

Installation description **will be available soon**.

Documentation
-------------

The documentation **will be available soon** `here
<http://retdec-python.readthedocs.org/en/latest/>`_.

Contact and Support
-------------------

I will be very glad to get your feedback, `pull requests
<https://github.com/s3rvac/retdec-python/pulls>`_, `issues
<https://github.com/s3rvac/retdec-python/issues>`_, or a just simple *Thanks*.
Feel free to contact me for any questions you might have!

License
-------

Copyright (c) 2015 Petr Zemek (s3rvac@gmail.com) and contributors.

Distributed under the MIT license. See the `LICENSE
<https://github.com/s3rvac/retdec-python/blob/master/LICENSE>`_ file for more
details.

Access from Other Languages
---------------------------

If you want to access the `retdec.com <https://retdec.com>`_ decompilation
service from other languages, check out the following projects:

* `retdec-cpp <https://github.com/s3rvac/retdec-cpp>`_ - A library and tools
  for accessing the service from C++.
* `retdec-sh <https://github.com/s3rvac/retdec-sh>`_ - Scripts for accessing
  the service from shell.
