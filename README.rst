qPython
=======

qPython is a Python library providing support for interprocess communication between Python and kdb+ processes, it offers:

- Synchronous and asynchronous queries
- Convenient asynchronous callbacks mechanism
- Support for kdb+ protocol and types: v3.0, v2.6, v<=2.5
- Uncompression of the IPC data stream
- Internal representation of data via numpy arrays (lists, complex types) and numpy data types (atoms)
- Supported on Python 2.7/3.3/3.4 and numpy 1.8
 
For more details please refer to the `documentation`_.


Installation
------------

To install qPython from PyPI:

``$ pip install qpython``

**Please do not use old PyPI package name: exxeleron-qpython.**


Building package
----------------

Documentation
~~~~~~~~~~~~~

qPython documentation is generated with help of `Sphinx`_ document generator.
In order to build the documentation, including the API docs, execute: 
``make html`` from the doc directory.

Documentation is built into the: ``doc/build/html/`` directory.


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

qPython requires numpy 1.8 to run.

Optional requirements have to be met to provide additional features:

- tune performance of critical parts of the code:

  - Cython 0.20.1

- support serialization/deserialization of ``pandas.Series`` and ``pandas.DataFrame``

  - pandas 0.14.0
  
- run Twisted sample:

  - Twisted 13.2.0

- build documentation via Sphinx:

  - Sphinx 1.2.3
  - mock 1.0.1

Required libraries can be installed using `pip`_.

To install all the required dependencies, execute: 
``pip install -r requirements.txt``

Minimal set of required dependencies can be installed by executing: 
``pip install -r requirements-minimal.txt``

.. _Cython: http://cython.org/
.. _Sphinx: http://sphinx-doc.org/
.. _pip: http://pypi.python.org/pypi/pip
.. _documentation: http://qpython.readthedocs.org/en/latest/
