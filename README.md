## qPython 1.0 Beta

qPython is a Python library providing support for interprocess communication between Python and kdb+ processes, it offers:
- Synchronous and asynchronous queries
- Convenient asynchronous callbacks mechanism
- Support for kdb+ protocol and types: v3.0, v2.6, v<=2.5
- Uncompression of the IPC data stream
- Internal representation of data via numpy arrays (lists, complex types) and numpy data types (atoms)
- Supported on Python 2.7 and numpy 1.8


### Building package

#### Compile Cython extensions

qPython utilizes [Cython](http://cython.org/) to tune performance critical parts of the code.

Instructions:
 - Execute:
   `python setup.py build_ext --inplace`


#### Build binary distribution

Instructions:
 - Execute:
   `python setup.py bdist`


#### Testing

qPython uses py.test as a test runner for unit tests.

Instructions:
 - Make sure that top directory is included in the `PYTHONPATH`
 - Execute: `py.test`


#### Requirements
 - numpy 1.8
 - Cython 0.20.1


Required libraries can be installed using [pip](https://pypi.python.org/pypi/pip).
Execute: `pip install -r requirements.txt`