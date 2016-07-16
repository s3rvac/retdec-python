.. title:: Library

Library
=======

This page describes the `retdec-python <https://github.com/s3rvac/retdec-python>`_ library and its API.

Organization
------------

The base package is ``retdec``. Everything that the library provides is inside this package.

Authentication
--------------

The library needs to authenticate you to `retdec.com <https://retdec.com>`_. To specify your API key, either pass it as a parameter when creating a resource:

.. code-block:: python

    decompiler = retdec.decompiler.Decompiler(api_key='YOUR-API-KEY')

or set the ``RETDEC_API_KEY`` environment variable:

.. code::

    $ export RETDEC_API_KEY=YOUR-API-KEY

An advantage of the environment variable is that you do not need to specify the API key every time you use the library:

.. code-block:: python

    decompiler = retdec.decompiler.Decompiler()

Error Handling
--------------

The library uses exceptions to signalize errors. Every custom exception raised by the library inherits from :class:`retdec.exceptions.RetdecError`, which you can use to catch all custom exceptions raised by the library:

.. code-block:: python

    try:
        # ...
    except retdec.exceptions.RetdecError as ex:
        # Handle the error.

See the :mod:`retdec.exceptions` module for a list of all custom exceptions.

Decompiler
----------

The :mod:`retdec.decompiler` module provides access to the `decompilation service <https://retdec.com/api/docs/decompiler.html>`_. It allows you to decompile binary files into a high-level language representation, such as C.

Creating a Decompiler
^^^^^^^^^^^^^^^^^^^^^

The decompiler is represented by the :class:`retdec.decompiler.Decompiler` class:

.. code-block:: python

    decompiler = retdec.decompiler.Decompiler(api_key='YOUR-API-KEY')

Starting a Decompilation
^^^^^^^^^^^^^^^^^^^^^^^^

To start a decompilation of a file, call :func:`~retdec.decompiler.Decompiler.start_decompilation()`:

.. code-block:: python

    decompilation = decompiler.start_decompilation(input_file=FILE)

``FILE`` is either a path to the file or a file-like object. For a complete list of parameters that you can use when starting a decompilation, see the description of :func:`~retdec.decompiler.Decompiler.start_decompilation()`.

The returned object is an instance of :class:`retdec.decompilation.Decompilation`.

Waiting For the Decompilation To Finish
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the :func:`~retdec.decompiler.Decompiler.start_decompilation()` call above returns, the decompilation has been automatically started. To wait until it finishes, call :func:`~retdec.decompilation.Decompilation.wait_until_finished()`:

.. code-block:: python

    decompilation.wait_until_finished()

If you want to track the decompilation progress (e.g. by showing a progress bar or displaying the log), you can pass a callback function to :func:`~retdec.decompilation.Decompilation.wait_until_finished()`:

.. code-block:: python

    def show_progress(decompilation):
        print(decompilation.get_completion())

    decompilation.wait_until_finished(
        callback=show_progress
    )

When the status of the decompilation changes (e.g. it moves to another phase), the callback is automatically called with the decompilation being passed as its parameter.

Downloading Outputs
^^^^^^^^^^^^^^^^^^^

To obtain the generated high-level language (HLL) code as a string, call :func:`~retdec.decompilation.Decompilation.get_hll_code()`:

.. code-block:: python

    print(decompilation.get_hll_code())

Alternatively, you can call :func:`~retdec.decompilation.Decompilation.save_hll_code()`, which obtains and saves the generated HLL code into the given directory:

.. code-block:: python

    decompilation.save_hll_code('/home/user/downloads')

Apart from obtaining the HLL code, you can also get the disassembled code or, in the ``c`` mode, the compiled version of the input C file. See the description of :class:`~retdec.decompilation.Decompilation` for more details.

For a complete example, take a look the `retdec/tools/decompiler.py <https://github.com/s3rvac/retdec-python/blob/master/retdec/tools/decompiler.py>`_ file. It is an implementation of the :ref:`decompiler` script.

Fileinfo
--------

The :mod:`retdec.fileinfo` module provides access to the `file-analyzing service <https://retdec.com/api/docs/fileinfo.html>`_. It allows you to obtain information about binary files.

Creating an Analyzer
^^^^^^^^^^^^^^^^^^^^

The analyzer is represented by the :class:`retdec.fileinfo.Fileinfo` class:

.. code-block:: python

    fileinfo = retdec.fileinfo.Fileinfo(api_key='YOUR-API-KEY')

Starting an Analysis
^^^^^^^^^^^^^^^^^^^^

To start an analysis of a file, call :func:`~retdec.fileinfo.Fileinfo.start_analysis()` with a file to be analyzed:

.. code-block:: python

    analysis = fileinfo.start_analysis(input_file=FILE)

``FILE`` is either a path to the file or a file-like object. Optionally, you can pass the ``verbose=True`` argument, which makes the analysis to obtain all available information about the file.

The returned object is an instance of :class:`retdec.analysis.Analysis`.

Waiting For the Analysis To Finish
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the :func:`~retdec.fileinfo.Fileinfo.start_analysis()` call above returns, the analysis has been automatically started. To wait until it finishes, call :func:`~retdec.analysis.Analysis.wait_until_finished()`:

.. code-block:: python

    analysis.wait_until_finished()

Obtaining the Results of the Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To obtain the output from the analysis, call :func:`~retdec.analysis.Analysis.get_output()`:

.. code-block:: python

    print(analysis.get_output())

For a complete example, take a look at the `retdec/tools/fileinfo.py <https://github.com/s3rvac/retdec-python/blob/master/retdec/tools/fileinfo.py>`_ file. It is an implementation of the :ref:`fileinfo` script.

Test
----

Access to the `testing service <https://retdec.com/api/docs/test.html>`_ is provided by the :mod:`retdec.test` module.

Authentication
^^^^^^^^^^^^^^

To check whether you can authenticate successfully, use :func:`retdec.test.Test.auth()`:

.. code-block:: python

    test = retdec.test.Test(api_key='YOUR-API-KEY')
    try:
        test.auth()
        print('authentication succeeded')
    except retdec.exceptions.AuthenticationError as ex:
        print('authentication failed:', ex)

Parameter Passing
^^^^^^^^^^^^^^^^^

To check that parameters are passed correctly when performing requests to the `retdec.com API <https://retdec.com/api/>`_, use :func:`retdec.test.Test.echo()`:

.. code-block:: python

    test = retdec.test.Test(api_key='YOUR-API-KEY')
    result = test.echo(param='value')
    print(result)  # Prints {'param': 'value'}.
