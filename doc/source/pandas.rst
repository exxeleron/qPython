.. _pandas:

Pandas integration
==================

The `qPython` allows user to use ``pandas.DataFrame`` and ``pandas.Series``
instead of ``numpy.recarray`` and ``numpy.ndarray`` to represent ``q`` tables
and vectors.

In order to instrument `qPython` to use `pandas <http://pandas.pydata.org/>`_ data types user has to set
``pandas`` flag while:

- creating :class:`.qconnection.QConnection` instance,
- executing synchronous query: :meth:`~qpython.qconnection.QConnection.sendSync`,
- or retrieving data from q: :meth:`~qpython.qconnection.QConnection.receive`.

For example:
::

    >>> with qconnection.QConnection(host = 'localhost', port = 5000, pandas = True) as q:
    >>>     ds = q('(1i;0Ni;3i)', pandas = True)
    >>>     print(ds)
    0     1
    1   NaN
    2     3
    dtype: float64
    >>>     print(ds.meta)
    metadata(qtype=6)

    >>>     df =  q('flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))')
    >>>     print(df)
             name   iq           fullname
    0        Dent   98        Arthur Dent
    1  Beeblebrox   42  Zaphod Beeblebrox
    2     Prefect  126       Ford Prefect
    >>>     print(df.meta)
    metadata(iq=7, fullname=0, qtype=98, name=11)
    >>>     print(q('type', df))
    98

    >>>     df =  q('([eid:1001 0N 1003;sym:`foo`bar`] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))')
    >>>     print(df)
             pos      dates
    eid  sym
    1001 foo  d1 2001-01-01
    NaN  bar  d2 2000-05-01
    1003      d3        NaT
    >>>     print(df.meta)
    metadata(dates=14, qtype=99, eid=7, sym=11, pos=11)
    >>>     print(q('type', df))
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


Type hinting
************

`qPython` applies following heuristic to determinate conversion between pandas
and q types:

- ``pandas.DataFrame`` are serialized to q tables,

- ``pandas.Series`` are serialized to q lists according to these rules:

  - type of q list is determinate based on series `dtype`,
  - if mapping based on `dtype` is ambiguous (e.g. `dtype` is `object`),
    q type is determined by type of the first element in the array.


User can overwrite the default type mapping, by setting the ``meta`` attribute
and provide additional information for the serializer.

Lists conversions
+++++++++++++++++

By default, series of ``datetime64`` is mapped to q timestamp::

    pandas.Series(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), numpy.datetime64('nat', 'ms')]))
    # 2000.01.04D05:36:57.600000000 0N (type 12h)

``meta`` attribute, can be used to change this and convert the series to, for
example, q date list::

    l = pandas.Series(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), numpy.datetime64('nat', 'ms')]))
    l.meta = MetaData(qtype = QDATE_LIST)
    # 2000.01.04 0N (type 14h)


Similarly, the series of ``float64`` is mapped to q float (double precision)
vector::

    l = pandas.Series([1, numpy.nan, 3])
    # 1 0n 3 (type 9h)

This can be overwritten to convert the list to integer vector::

    l = pandas.Series([1, numpy.nan, 3])
    l.meta = MetaData(qtype = QINT_LIST)
    # 1 0N 3i (type 6h)


Table columns
+++++++++++++

Type hinting mechanism is useful for specifying the conversion rules for columns
in the table. This can be used either to enforce the type conversions or
provide information for ambiguous mappings.
::

    t = pandas.DataFrame(OrderedDict((('pos', pandas.Series(['A', 'B', 'C'])),
                                      ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'))))))

    # pos dates
    # ---------------------------------
    # A   2001.01.01D00:00:00.000000000
    # B   2000.05.01D00:00:00.000000000
    # C
    #
    # meta:
    # c    | t f a
    # -----| -----
    # pos  | c
    # dates| p

    t = pandas.DataFrame(OrderedDict((('pos', pandas.Series(['A', 'B', 'C'])),
                                      ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'))))))

    t.meta = MetaData(pos = QSYMBOL_LIST, dates = QDATE_LIST)

    # pos dates
    # --------------
    # A   2001.01.01
    # B   2000.05.01
    # C
    #
    # meta:
    # c    | t f a
    # -----| -----
    # pos  | s
    # dates| d


Keyed tables
++++++++++++

By default, ``pandas.DataFrame`` is represented as a q table. During the
serialization index information is discarded::

    t = pandas.DataFrame(OrderedDict((('eid', pandas.Series(numpy.array([1001, 1002, 1003]))),
                                      ('pos', pandas.Series(numpy.array(['d1', 'd2', 'd3']))),
                                      ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'))))))
    t.reset_index(drop = True)
    t.set_index(['eid'], inplace = True)
    t.meta = MetaData(pos = QSYMBOL_LIST, dates = QDATE_LIST)

    # pos dates
    # --------------
    # d1  2001.01.01
    # d2  2000.05.01
    # d3
    #
    # meta:
    # c    | t f a
    # -----| -----
    # pos  | s
    # dates| d


In order to preserve the index data and represent ``pandas.DataFrame`` as a q
keyed table, use type hinting mechanism to enforce the serialization rules::

    t = pandas.DataFrame(OrderedDict((('eid', pandas.Series(numpy.array([1001, 1002, 1003]))),
                                      ('pos', pandas.Series(numpy.array(['d1', 'd2', 'd3']))),
                                      ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'))))))
    t.reset_index(drop = True)
    t.set_index(['eid'], inplace = True)
    t.meta = MetaData(pos = QSYMBOL_LIST, dates = QDATE_LIST, qtype = QKEYED_TABLE)

    # eid | pos dates
    # ----| --------------
    # 1001| d1  2001.01.01
    # 1002| d2  2000.05.01
    # 1003| d3
    #
    # meta:
    # c    | t f a
    # -----| -----
    # eid  | j
    # pos  | s
    # dates| d

