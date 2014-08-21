qPython 1.0 Beta
================

qPython is a Python library providing support for interprocess communication between Python and kdb+ processes, it offers:

- Synchronous and asynchronous queries
- Convenient asynchronous callbacks mechanism
- Support for kdb+ protocol and types: v3.0, v2.6, v<=2.5
- Uncompression of the IPC data stream
- Internal representation of data via numpy arrays (lists, complex types) and numpy data types (atoms)
- Supported on Python 2.7 and numpy 1.8
 
For more details please refer to the `documentation`_.

Building package
----------------

Compile Cython extensions
~~~~~~~~~~~~~~~~~~~~~~~~~

qPython utilizes `Cython`_ to tune performance critical parts of the code.

Instructions: 

- Execute: ``python setup.py build_ext --inplace``


Build binary distribution
~~~~~~~~~~~~~~~~~~~~~~~~~

Instructions: 

- Execute: ``python setup.py bdist``


Testing
~~~~~~~

qPython uses py.test as a test runner for unit tests.

Instructions:

- Make sure that top directory is included in the ``PYTHONPATH``
- Execute: ``py.test``


Requirements
~~~~~~~~~~~~

To run, qPython requires:

- numpy 1.8

To tune performance critical parts of the code, additional requirements have to be met:

- Cython 0.20.1

To run Twisted sample, qPython requires:

- Twisted 13.2.0

Required libraries can be installed using `pip`_.

To install all the required dependencies, execute: ``pip install -r requirements.txt``

To install minimal set of required dependencies, execute: ``pip install -r requirements-minimal.txt``

.. _Cython: http://cython.org/
.. _pip: https://pypi.python.org/pypi/pip
.. _documentation: https://github.com/exxeleron/qPython/blob/master/doc
