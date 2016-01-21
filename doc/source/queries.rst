.. _queries:

Queries
=======

The `qPython` library supports both synchronous and asynchronous queries.

Synchronous query waits for service response and blocks requesting process until
it receives the response. Asynchronous query does not block the requesting 
process and returns immediately without any result. The actual query result can 
be obtained either by issuing a corresponding request later on, or by setting up
a listener to await and react accordingly to received data.

The `qPython` library provides following API methods in the 
:class:`.QConnection` class to interact with q:

- :func:`~qpython.qconnection.QConnection.sync` - executes a synchronous query 
  against the remote q service,
- :func:`~qpython.qconnection.QConnection.async` - executes an asynchronous 
  query against the remote q service,
- :func:`~qpython.qconnection.QConnection.query` - executes a query against the
  remote q service.

These methods have following parameters:

- ``query`` is the definition of the query to be executed,
- ``parameters`` is a list of additional parameters used when executing given 
  query.

In typical use case, ``query`` is the name of the function to call and 
``parameters`` are its parameters. When parameters list is empty the query can 
be an arbitrary q expression (e.g. ``0 +/ til 100``).


Synchronous queries
*******************

Executes a q expression:
        
    >>> print(q.sync('til 10'))
    [0 1 2 3 4 5 6 7 8 9]

Executes an anonymous q function with a single parameter:

    >>> print(q.sync('{til x}', 10))
    [0 1 2 3 4 5 6 7 8 9]
    
Executes an anonymous q function with two parameters:

    >>> print(q.sync('{y + til x}', 10, 1))
    [ 1  2  3  4  5  6  7  8  9 10]
    >>> print(q.sync('{y + til x}', *[10, 1]))
    [ 1  2  3  4  5  6  7  8  9 10]

The :class:`.QConnection` class implements the 
:func:`~qpython.qconnection.QConnection.__call__` method. This allows 
:class:`.QConnection` instance to be called as a function:
        
    >>> print(q('{y + til x}', 10, 1))
    [ 1  2  3  4  5  6  7  8  9 10]

    
Asynchronous queries
********************

Calls a anonymous function with a single parameter:
        
    >>> q.async('{til x}', 10)

Executes a q expression:

    >>> q.async('til 10')

.. note:: The asynchronous query doesn't fetch the result. Query result has
          to be retrieved explicitly.

In order to retrieve query result (for the 
:func:`~qpython.qconnection.QConnection.async` or 
:func:`~qpython.qconnection.QConnection.query` methods), one has to call:
 
- :func:`~qpython.qconnection.QConnection.receive` method, which reads next 
  message from the remote q service.

For example:   

- Retrieves query result along with meta-information:
    
>>> q.query(qconnection.MessageType.SYNC,'{x}', 10)
>>> print(q.receive(data_only = False, raw = False))
QMessage: message type: 2, data size: 13, is_compressed: False, data: 10

- Retrieves parsed query result:

>>> q.query(qconnection.MessageType.SYNC,'{x}', 10)
>>> print(q.receive(data_only = True, raw = False))
10

>>> q.sync('asynchMult:{[a;b] res:a*b; (neg .z.w)(res) }')
>>> q.async('asynchMult', 2, 3)
>>> print(q.receive())
6

- Retrieves not-parsed (raw) query result:

>>> from binascii import hexlify
>>> q.query(qconnection.MessageType.SYNC,'{x}', 10)
>>> print(hexlify(q.receive(data_only = True, raw = True)))
fa0a000000


Type conversions configuration
******************************

Type conversion options can be overwritten while:

- executing synchronous query: :meth:`~qpython.qconnection.QConnection.sync`
- executing asynchronous query: :meth:`~qpython.qconnection.QConnection.async`
- retrieving data from q: :meth:`~qpython.qconnection.QConnection.receive`

These methods accepts the `options` keywords arguments::

    >>> query = "{[x] 0Nd, `date$til x}"
    
    >>> # retrieve function call as raw byte buffer
    >>> from binascii import hexlify
    >>> print(binascii.hexlify(q(query, 5, raw = True)))
    0e0006000000000000800000000001000000020000000300000004000000

    >>> # perform a synchronous call and parse dates vector to numpy array
    >>> print(q.sync(query, 5, numpy_temporals = True))
    ['NaT' '2000-01-01' '2000-01-02' '2000-01-03' '2000-01-04' '2000-01-05']

    >>> # perform a synchronous call
    >>> q.query(qconnection.MessageType.SYNC, query, 3)
    >>> # retrieve query result and represent dates vector as raw data wrapped in QTemporalList
    >>> print(q.receive(numpy_temporals = False))
    [NaT [metadata(qtype=-14)] 2000-01-01 [metadata(qtype=-14)]
     2000-01-02 [metadata(qtype=-14)] 2000-01-03 [metadata(qtype=-14)]]
    
    >>> # serialize single element strings as q characters 
    >>> print(q.sync('{[x] type each x}', ['one', 'two', '3'], single_char_strings = False))
    [ 10,  10, -10]
    
    >>> # serialize single element strings as q strings 
    >>> print(q.sync('{[x] type each x}', ['one', 'two', '3'], single_char_strings = True))
    [10, 10, 10]
