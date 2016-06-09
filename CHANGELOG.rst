Changelog
=========

dev
---

* Added support for passing a PDB file to decompilations.
* Added a new method to the ``Test`` service: ``echo()``. It echoes back the
  parameters passed via the `test/echo
  <https://retdec.com/api/docs/test.html#parameter-passing>`_ service.
* Added a `summary
  <https://retdec-python.readthedocs.io/en/latest/status.html>`_ of the
  supported parts of the `retdec.com API
  <https://retdec.com/api/docs/index.html>`_ into the `documentation
  <https://retdec-python.readthedocs.io/en/latest/>`_.
* ``Decompiler.start_decompilation()`` and ``Fileinfo.start_analysis()`` raise
  ``MissingParameterError`` when the input file is not given.
* Re-formatted the progress-log output from the ``decompiler`` tool to ensure
  that the ``[OK]`` parts are aligned properly.

0.1 (2015-09-13)
----------------

Initial release.
