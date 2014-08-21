### Basic types

While deserializing, atom values from q are mapped according to table:

```
| q type    | q num type | q  type   | Python type        |
|-----------|------------|-----------|--------------------|
| bool      | -1         | boolean   | numpy.bool_        |
| byte      | -4         | byte      | numpy.byte         |
| short     | -5         | short     | numpy.int16        |
| int       | -6         | integer   | numpy.int32        |
| long      | -7         | long      | numpy.int64        |
| real      | -8         | real      | numpy.float32      |
| double    | -9         | float     | numpy.float64      |
| character | -10        | character | single element str |
```

Serialization of atom Python data to q is ambiguous.

```
| Python type        | q type    |
|--------------------|-----------|
| bool               | bool      |
| ---                | byte      |
| ---                | short     |
| int                | int       |
| long               | long      |
| ---                | real      |
| double             | float     |
| numpy.bool         | bool      |
| numpy.byte         | byte      |
| numpy.int16        | short     |
| numpy.int32        | int       |
| numpy.int64        | long      |
| numpy.float32      | real      |
| numpy.float64      | float     |
| single element str | character |
```

### Lists
Deserialized q lists are mapped to `numpy` arrays. The resulting `numpy` array contains a type indicator linked to original q type. 

Generic lists are represented as a Python lists.

While serializing Python data to q following rules are applied:
- `numpy` arrays with type code indicator are serialized to proper q list
- ambiguous mapping for `numpy` arrays is determined by the first element of the array
- Python lists and tuples are represented as q generic lists


The `qcollection` module provides an utility method:

```python
def qlist(array, adjust_dtype = True, **meta)
```

which simplifies creation of `QList` objects. This method:
- creates a `numpy` view `QList`
- converts the input `numpy` array if the original `dtype` doesn’t match requested conversion, e.g.: `numpy.int16` array requested to be represented as a `QLONG_LIST`
- optional meta information, e.g.: q type indicator: `qtype=QLONG_LIST`

For example:
```python
# 1 2 3
qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype = QLONG_LIST)
qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST)

# (0x01;0x02;0xff)
qlist(numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte), qtype = QBYTE_LIST)
qlist(numpy.array([0x01, 0x02, 0xff]), qtype = QBYTE_LIST)
```

### String and symbols
In order to distinguish symbols and strings on the Python side, following rules apply:
- q symbols are represented as `numpy.string_` type
- q strings are mapped to plain Python strings

```python
# `quickbrownfoxjumpsoveralazydog
numpy.string_('quickbrownfoxjumpsoveralazydog')

# "quick brown fox jumps over a lazy dog"
'quick brown fox jumps over a lazy dog'
```

### Temporal types
Atom q temporal types are represented as instances of `QTemporal` class, which is a thin wrapper around the `numpy.datetime64` and `numpy.timedelta64`. The following table summarizes mapping between q temporal types and their Python counterparties (along with `numpy` resolution).

```
| kdb+ type | Python type | numpy type        | numpy resolution |
|-----------|-------------|-------------------|------------------|
| date      | QTemporal   | numpy.datetime64  | D                |
| time      | QTemporal   | numpy.timedelta64 | ms               |
| datetime  | QTemporal   | numpy.datetime64  | ms               |
| month     | QTemporal   | numpy.datetime64  | M                |
| minute    | QTemporal   | numpy.timedelta64 | m                |
| second    | QTemporal   | numpy.timedelta64 | s                |
| timestamp | QTemporal   | numpy.datetime64  | ns               |
| timespan  | QTemporal   | numpy.timedelta64 | ns               |
```

Lists of temporal values are represented as instances of `QTemporalList` class. This class wraps the raw q representation of temporal data (i.e. `long`s for `timestamp`s, `int`s for `month`s etc.) and provides accessors which allow to convert raw data to `QTemporal` instances in a lazy manner.

In addition, the `qtemporal` module provides an utility method, which converts a `numpy.array` to q temporal list and enriches object instance with provided meta data:

```python
def qtemporallist(array, **meta)
```

For example:
```python
# 2001.01.01 2000.05.01 0Nd
qtemporallist(numpy.array([to_raw_qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE), to_raw_qtemporal(numpy.datetime64('2000-05-01', 'D'), qtype=QDATE), qnull(QDATE)]), qtype=QDATE_LIST)
qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)

# 2000.01.04D05:36:57.600 0Np
qtemporallist(numpy.array([long(279417600000000), qnull(QTIMESTAMP)]), qtype=QTIMESTAMP_LIST)
```


### guid
The q type GUID is mapped to standard Python `UUID` class.


### Dictionaries
Q dictionaries represent q dictionaries with custom `QDictionary` class, which internally stores keys and values in two `numpy` arrays.

Example:
```python
# 1 2!`abc`cdefgh
QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
            qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST))


# (1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))
QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), '4'],
            [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), '456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]])
```

### Tables
The q tables (keyed and non-keyed) are translated into custom type `QTable` (derived from `numpy.recarray`). Internal table data is stored as a `numpy` array separately for each column. This mimics the internal representation of tables in q.

The `qPython` library provides a utility function:

```python
qcollection.qtable(columns, data, **meta)
```

which simplifies creation of `QTables` using provided:
- column names
- data for each column
- meta data (optional)

For example:
```python
# flip `abc`def!(1 2 3; 4 5 6)
qtable(qlist(numpy.array(['abc', 'def']), qtype = QSYMBOL_LIST), 
      [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST), 
       qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)])

# ([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))
qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
      [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
       qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)])
```

The keyed tables are represented via `QKeyedTable` instances, in which both keys and values are stored as a separate `QTable` instances.

For example:
```python
# ([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))
QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype = QSYMBOL_LIST),
                   [qlist(numpy.array([1001, 1002, 1003]), qtype = QLONG_LIST)]),
            qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                   [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
                    qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype = QDATE_LIST)]))
```

### Lambdas
The q lambda is mapped to custom Python class `QLambda`.

```python
# {x+y}
QLambda('{x+y}')

# {x+y} [3]
QLambda('{x+y}', numpy.int64(3))
```

### Exceptions
The q errors are represented as instances of `QException` class.


### Null values

Please note that `null` values are defined as:

```python
_QNULL1 = numpy.int8(-2**7)
_QNULL2 = numpy.int16(-2**15)
_QNULL4 = numpy.int32(-2**31)
_QNULL8 = numpy.int64(-2**63)
_QNAN32 = numpy.fromstring('\x00\x00\xc0\x7f', dtype=numpy.float32)[0]
_QNAN64 = numpy.fromstring('\x00\x00\x00\x00\x00\x00\xf8\x7f', dtype=numpy.float64)[0]
_QNULL_BOOL = numpy.bool_(False)
_QNULL_SYM = numpy.string_('')
_QNULL_GUID = uuid.UUID('00000000-0000-0000-0000-000000000000')
```

Corresponding `null` values therefore become:

```
| qPython type | q null value | Python representation |
|--------------|--------------|-----------------------|
| QGUID        | 0Ng          | _QNULL_GUID           |
| QBOOL        | 0b           | _QNULL_BOOL           |
| QBYTE        | 0x00         | _QNULL1               |
| QSHORT       | 0Nh          | _QNULL2               |
| QINT         | 0N           | _QNULL4               |
| QLONG        | 0Nj          | _QNULL8               |
| QFLOAT       | 0Ne          | _QNAN32               |
| QDOUBLE      | 0n           | _QNAN64               |
| QSTRING      | " "          | ' '                   |
| QSYMBOL      | `            | _QNULL_SYM            |
| QMONTH       | 0Nm          | _QNULL4               |
| QDATE        | 0Nd          | _QNULL4               |   
| QDATETIME    | 0Nz          | _QNAN64               |   
| QMINUTE      | 0Nu          | _QNULL4               |   
| QSECOND      | 0Nv          | _QNULL4               |   
| QTIME        | 0Nt          | _QNULL4               |   
| QTIMESPAN    | 0Nn          | _QNULL8               |   
| QTIMESTAMP   | 0Np          | _QNULL8               | 
```