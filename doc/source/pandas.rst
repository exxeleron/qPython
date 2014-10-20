Pandas integration
==================

The `qPython` allows user to use ``pandas.DataFrame`` and ``pandas.Series``
instead of ``numpy.recarray`` and ``numpy.ndarray`` to represent ``q`` tables
and vectors.

In order to instrument `qPython` to use `pandas`_ data types user has to set
``pandas`` flag while:

- creating :class:`.qconnection.QConnection` instance,
- executing synchronous query: :meth:`~qpython.qconnection.QConnection.sync`,
- or retrieving data from q: :meth:`~qpython.qconnection.QConnection.receive`.

For example:
::

    >>> with qconnection.QConnection(host = 'localhost', port = 5000, pandas = True) as q:
    >>>     ds = q('(1i;0Ni;3i)', pandas = True)
    >>>     print ds
    0     1
    1   NaN
    2     3
    dtype: float64
    >>>     print ds.meta
    metadata(qtype=6)

    >>>     df =  q('flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))')
    >>>     print df
             name   iq           fullname
    0        Dent   98        Arthur Dent
    1  Beeblebrox   42  Zaphod Beeblebrox
    2     Prefect  126       Ford Prefect
    >>>     print df.meta
    metadata(iq=7, fullname=0, qtype=98, name=11)
    >>>     print q('type', df)
    98

    >>>     df =  q('([eid:1001 0N 1003;sym:`foo`bar`] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))')
    >>>     print df
             pos      dates
    eid  sym
    1001 foo  d1 2001-01-01
    NaN  bar  d2 2000-05-01
    1003      d3        NaT
    >>>     print df.meta
    metadata(dates=14, qtype=99, eid=7, sym=11, pos=11)
    >>>     print q('type', df)
    99


Data conversions
****************

If ``pandas`` flag is set, `qPython` converts the data according to following
rules:

- ``q`` vectors are represented as ``pandas.Series``:

  - ``pandas.Series`` is initialized with ``numpy.ndarray`` being result of
    parsing with ``numpy_temporals`` flag set to ``True`` (to ensure that
    temporal vectors are represented as numpy ``datetime64``/``timedelta64``
    arrays).
  - q nulls are replaced with ``numpy.NaN``. This can result in type promotion
    as described in `pandas documentation <http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na>`_.
  - ``pandas.Series`` is enriched with custom attribute ``meta``
    (:class:`qpython.MetaData`), which contains `qtype` of the vector. Note
    that this information is used while serializaing ``pandas.Series`` instance
    to IPC protocol.


- tables are represented as ``pandas.DataFrame`` instances:

  - individual columns are represented as ``pandas.Series``.
  - ``pandas.DataFrame`` is enriched with custom attribute ``meta``
    (:class:`qpython.MetaData`), which lists `qtype` for each column in table.
    Note that this information is used during ``pandas.DataFrame`` serialization.

- keyed tables are backed as ``pandas.DataFrame`` instances as well:

  - index for ``pandas.DataFrame`` is created from key columns.
  - ``pandas.DataFrame`` is enriched with custom attribute ``meta``
    (:class:`qpython.MetaData`), which lists `qtype` for each column in table,
    including index ones. Note that this information is used during
    ``pandas.DataFrame`` serialization.


.. _pandas: http://pandas.pydata.org/

