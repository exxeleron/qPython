#
#  Copyright (c) 2011-2014 Exxeleron GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from qpython.qtype import *  # @UnusedWildImport
from qpython import MetaData
from qpython.qtemporal import qtemporal, from_raw_qtemporal, to_raw_qtemporal


class QList(numpy.ndarray):
    '''An array object represents a q vector.'''

    def _meta_init(self, **meta):
        '''Initialises the meta-information.'''
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.dtype, self.meta.qtype, self.tostring()))

    def __array_finalize__(self, obj):
        self.meta = MetaData() if obj is None else getattr(obj, 'meta', MetaData())



class QTemporalList(QList):
    '''An array object represents a q vector of datetime objects.'''

    def __getitem__(self, idx):
        return qtemporal(from_raw_qtemporal(numpy.ndarray.__getitem__(self, idx), -abs(self.meta.qtype)), qtype = -abs(self.meta.qtype))

    def __setitem__(self, idx, value):
        numpy.ndarray.__setitem__(self, idx, to_raw_qtemporal(value, - -abs(self.meta.qtype)))

    def raw(self, idx):
        '''Gets the raw representation of the datetime object at the specified 
        index.
        
           >>> t = qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)
           >>> print(t[0])
           2001-01-01 [metadata(qtype=-14)]
           >>> print(t.raw(0))
           366
        
        :Parameters:
         - `idx` (`integer`) - array index of the datetime object to be retrieved
         
        :returns: raw representation of the datetime object
        '''
        return numpy.ndarray.__getitem__(self, idx)



def get_list_qtype(array):
    '''Finds out a corresponding qtype for a specified `QList`/`numpy.ndarray` 
    instance.
    
    :Parameters:
     - `array` (`QList` or `numpy.ndarray`) - array to be checked
    
    :returns: `integer` - qtype matching the specified array object
    '''
    if not isinstance(array, numpy.ndarray):
        raise ValueError('array parameter is expected to be of type: numpy.ndarray, got: %s' % type(array))

    if isinstance(array, QList):
        return -abs(array.meta.qtype)

    qtype = None

    if str(array.dtype) in ('|S1', '<U1', '>U1', '|U1') :
        qtype = QCHAR

    if qtype is None:
        qtype = Q_TYPE.get(array.dtype.type, None)

    if qtype is None and array.dtype.type in (numpy.datetime64, numpy.timedelta64):
        qtype = TEMPORAL_PY_TYPE.get(str(array.dtype), None)

    if qtype is None:
        # determinate type based on first element of the numpy array
        qtype = Q_TYPE.get(type(array[0]), QGENERAL_LIST)

    return qtype



def qlist(array, adjust_dtype = True, **meta):
    '''Converts an input array to q vector and enriches object instance with 
    meta data.

    Returns a :class:`.QList` instance for non-datetime vectors. For datetime 
    vectors :class:`.QTemporalList` is returned instead.

    If parameter `adjust_dtype` is `True` and q type retrieved via 
    :func:`.get_list_qtype` doesn't match one provided as a `qtype` parameter 
    guessed q type, underlying numpy.array is converted to correct data type.
    
    `qPython` internally represents ``(0x01;0x02;0xff)`` q list as:
    ``<class 'qpython.qcollection.QList'> dtype: int8 qtype: -4: [ 1  2 -1]``.
    This object can be created by calling the :func:`.qlist` with following 
    arguments:
    
    - `byte numpy.array`:
       
       >>> v = qlist(numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte))
       >>> print('%s dtype: %s qtype: %d: %s' % (type(v), v.dtype, v.meta.qtype, v))
       <class 'qpython.qcollection.QList'> dtype: int8 qtype: -4: [ 1  2 -1]
    
    - `int32 numpy.array` with explicit conversion to `QBYTE_LIST`:   
      
       >>> v = qlist(numpy.array([1, 2, -1]), qtype = QBYTE_LIST)
       >>> print('%s dtype: %s qtype: %d: %s' % (type(v), v.dtype, v.meta.qtype, v))
       <class 'qpython.qcollection.QList'> dtype: int8 qtype: -4: [ 1  2 -1]
    
    - plain Python `integer` list with explicit conversion to `QBYTE_LIST`:   
       
       >>> v = qlist([1, 2, -1], qtype = QBYTE_LIST)
       >>> print('%s dtype: %s qtype: %d: %s' % (type(v), v.dtype, v.meta.qtype, v))
       <class 'qpython.qcollection.QList'> dtype: int8 qtype: -4: [ 1  2 -1]

    - numpy datetime64 array with implicit conversion to `QDATE_LIST`:   
       
       >>> v = qlist(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'))
       >>> print('%s dtype: %s qtype: %d: %s' % (type(v), v.dtype, v.meta.qtype, v))
       <class 'qpython.qcollection.QList'> dtype: datetime64[D] qtype: -14: ['2001-01-01' '2000-05-01' 'NaT']
       
    - numpy datetime64 array with explicit conversion to `QDATE_LIST`:   
       
       >>> v = qlist(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'), qtype = QDATE_LIST)
       >>> print('%s dtype: %s qtype: %d: %s' % (type(v), v.dtype, v.meta.qtype, v))
       <class 'qpython.qcollection.QList'> dtype: datetime64[D] qtype: -14: ['2001-01-01' '2000-05-01' 'NaT']

    
    :Parameters:
     - `array` (`tuple`, `list`, `numpy.array`) - input array to be converted
     - `adjust_dtype` (`boolean`) - determine whether data type of vector should
       be adjusted if it doesn't match default representation. **Default**: ``True``
       
     .. note:: numpy `datetime64` and `timedelta64` arrays are not converted
               to raw temporal vectors if `adjust_dtype` is ``True``
    
    :Kwargs:
     - `qtype` (`integer` or `None`) - qtype indicator
     
    :returns: `QList` or `QTemporalList` - array representation of the list
    
    :raises: `ValueError` 
    '''
    if type(array) in (list, tuple):
        if meta and 'qtype' in meta and meta['qtype'] == QGENERAL_LIST:
            # force shape and dtype for generic lists
            tarray = numpy.ndarray(shape = len(array), dtype = numpy.dtype('O'))
            for i in range(len(array)):
                tarray[i] = array[i]
            array = tarray
        else:
            array = numpy.array(array)

    if not isinstance(array, numpy.ndarray):
        raise ValueError('array parameter is expected to be of type: numpy.ndarray, list or tuple. Was: %s' % type(array))

    qtype = None
    is_numpy_temporal = array.dtype.type in (numpy.datetime64, numpy.timedelta64)

    if meta and 'qtype' in meta:
        qtype = -abs(meta['qtype'])
        dtype = PY_TYPE[qtype]
        if adjust_dtype and dtype != array.dtype and not is_numpy_temporal:
            array = array.astype(dtype = dtype)

    qtype = get_list_qtype(array) if qtype is None else qtype
    meta['qtype'] = qtype

    is_raw_temporal = meta['qtype'] in [QMONTH, QDATE, QDATETIME, QMINUTE, QSECOND, QTIME, QTIMESTAMP, QTIMESPAN] \
                      and not is_numpy_temporal
    vector = array.view(QList) if not is_raw_temporal else array.view(QTemporalList)
    vector._meta_init(**meta)
    return vector



class QDictionary(object):
    '''Represents a q dictionary.
    
    Dictionary examples:
    
    >>> # q: 1 2!`abc`cdefgh
    >>> print(QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST), 
    ...                    qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST)))
    [1 2]!['abc' 'cdefgh']
       
    >>> # q: (1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))
    >>> print(QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), '4'], 
    ...                    [numpy.string_('one'), qlist(numpy.array([2, 3]), qtype=QLONG_LIST), '456', [numpy.int64(7), qlist(numpy.array([8, 9]), qtype=QLONG_LIST)]]))
    [1, 2, 3.234, '4']!['one', QList([2, 3], dtype=int64), '456', [7, QList([8, 9], dtype=int64)]]
    
    :Parameters:
     - `keys` (`QList`, `tuple` or `list`) - dictionary keys
     - `values` (`QList`, `QTable`, `tuple` or `list`) - dictionary values
    '''
    def __init__(self, keys, values):
        if not isinstance(keys, (QList, tuple, list, numpy.ndarray)):
            raise ValueError('%s expects keys to be of type: QList, tuple or list. Actual type: %s' % (self.__class__.__name__, type(keys)))
        if not isinstance(values, (QTable, QList, tuple, list, numpy.ndarray)):
            raise ValueError('%s expects values to be of type: QTable, QList, tuple or list. Actual type: %s' % (self.__class__.__name__, type(values)))
        if len(keys) != len(values):
            raise ValueError('Number of keys: %d doesn`t match number of values: %d' % (len(keys), len(values)))

        self.keys = keys
        self.values = values

    def __str__(self, *args, **kwargs):
        return '%s!%s' % (self.keys, self.values)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        idx = 0
        for key in self.keys:
            if key != other.keys[idx] or self.values[idx] != other.values[idx]:
                return False
            idx += 1

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def _find_key_(self, key):
        idx = 0
        for k in self.keys:
            if key == k:
                return idx
            idx += 1

        raise KeyError('QDictionary doesn`t contain key: %s' % key)

    def __getitem__(self, key):
        return self.values[self._find_key_(key)]

    def __setitem__(self, key, value):
        self.values[self._find_key_(key)] = value

    def __len__(self):
        return len(self.keys)

    def __iter__(self):
        return iter(self.keys)

    def items(self):
        '''Return a copy of the dictionary's list of ``(key, value)`` pairs.'''
        return [(self.keys[x], self.values[x]) for x in range(len(self.keys))]

    def iteritems(self):
        '''Return an iterator over the dictionary's ``(key, value)`` pairs.'''
        for x in range(len(self.keys)):
            yield (self.keys[x], self.values[x])

    def iterkeys(self):
        '''Return an iterator over the dictionary's keys.'''
        return iter(self.keys)

    def itervalues(self):
        '''Return an iterator over the dictionary's values.'''
        return iter(self.values)



class QTable(numpy.recarray):
    '''Represents a q table.
    
    Internal table data is stored as a `numpy.array` separately for each column.
    This mimics the internal representation of tables in q.
    '''
    def _meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __array_finalize__(self, obj):
        self.meta = MetaData() if obj is None else getattr(obj, 'meta', MetaData())



def qtable(columns, data, **meta):
    '''Creates a QTable out of given column names and data, and initialises the 
    meta data.
    
    :class:`.QTable` is represented internally by `numpy.core.records.recarray`.
    Data for each column is converted to :class:`.QList` via :func:`.qlist` 
    function. If qtype indicator is defined for a column, this information
    is used for explicit array conversion.
    
    Table examples:
  
      >>> # q: flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)
      >>> t = qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST), 
      ...     [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect'])), 
      ...      qlist(numpy.array([98, 42, 126], dtype=numpy.int64))])
      >>> print('%s dtype: %s meta: %s: %s' % (type(t), t.dtype, t.meta, t))
      <class 'qpython.qcollection.QTable'> dtype: [('name', 'S10'), ('iq', '<i8')] meta: metadata(iq=-7, qtype=98, name=-11): [('Dent', 98L) ('Beeblebrox', 42L) ('Prefect', 126L)]
      
      >>> # q: flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)
      >>> t = qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
      ...           [qlist(['Dent', 'Beeblebrox', 'Prefect'], qtype = QSYMBOL_LIST), 
      ...            qlist([98, 42, 126], qtype = QLONG_LIST)])
      >>> print('%s dtype: %s meta: %s: %s' % (type(t), t.dtype, t.meta, t))
      <class 'qpython.qcollection.QTable'> dtype: [('name', 'S10'), ('iq', '<i8')] meta: metadata(iq=-7, qtype=98, name=-11): [('Dent', 98L) ('Beeblebrox', 42L) ('Prefect', 126L)]
      
      >>> # q: flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)
      >>> t = qtable(['name', 'iq'],
      ...            [['Dent', 'Beeblebrox', 'Prefect'], 
      ...             [98, 42, 126]],
      ...            name = QSYMBOL, iq = QLONG)
      >>> print('%s dtype: %s meta: %s: %s' % (type(t), t.dtype, t.meta, t)) 
      <class 'qpython.qcollection.QTable'> dtype: [('name', 'S10'), ('iq', '<i8')] meta: metadata(iq=-7, qtype=98, name=-11): [('Dent', 98L) ('Beeblebrox', 42L) ('Prefect', 126L)]
      
      >>> # q: flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))
      >>> t = qtable(('name', 'iq', 'fullname'),
      ...            [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
      ...             qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
      ...             qlist(numpy.array(["Arthur Dent", "Zaphod Beeblebrox", "Ford Prefect"]), qtype = QSTRING_LIST)])
      <class 'qpython.qcollection.QTable'> dtype: [('name', 'S10'), ('iq', '<i8'), ('fullname', 'O')] meta: metadata(iq=-7, fullname=0, qtype=98, name=-11): [('Dent', 98L, 'Arthur Dent') ('Beeblebrox', 42L, 'Zaphod Beeblebrox') ('Prefect', 126L, 'Ford Prefect')]
    
    :Parameters:
     - `columns` (list of `strings`) - table column names 
     - `data` (list of lists) - list of columns containing table data
    
    :Kwargs:
     - `meta` (`integer`) - qtype for particular column 
    
    :returns: `QTable` - representation of q table
    
    :raises: `ValueError`
    '''
    if len(columns) != len(data):
        raise ValueError('Number of columns doesn`t match the data layout. %s vs %s' % (len(columns), len(data)))

    meta = {} if not meta else meta

    if not 'qtype' in meta:
        meta['qtype'] = QTABLE

    dtypes = []
    for i in range(len(columns)):
        column_name = columns[i] if isinstance(columns[i], str) else columns[i].decode("utf-8")
        
        if isinstance(data[i], str):
            # convert character list (represented as string) to numpy representation
            data[i] = numpy.array(list(data[i]), dtype = numpy.string_)
        if isinstance(data[i], bytes):
            data[i] = numpy.array(list(data[i].decode()), dtype = numpy.string_)

        if column_name in meta:
            data[i] = qlist(data[i], qtype = meta[column_name])
        elif not isinstance(data[i], QList):
            if type(data[i]) in (list, tuple):
                data[i] = qlist(data[i], qtype = QGENERAL_LIST)
            else:
                data[i] = qlist(data[i])

        
        meta[column_name] = data[i].meta.qtype
        dtypes.append((column_name, data[i].dtype))

    table = numpy.core.records.fromarrays(data, dtype = dtypes)
    table = table.view(QTable)

    table._meta_init(**meta)
    return table



class QKeyedTable(object):
    '''Represents a q keyed table.
    
    :class:`.QKeyedTable` is built with two :class:`.QTable`\s, one representing
    keys and the other values.
    
    Keyed tables example:
    
        >>> # q: ([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))
        >>> t = QKeyedTable(qtable(['eid'],
        ...                [qlist(numpy.array([1001, 1002, 1003]), qtype = QLONG_LIST)]),
        ...         qtable(['pos', 'dates'],
        ...                [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
        ...                 qlist(numpy.array([366, 121, qnull(QDATE)]), qtype = QDATE_LIST)]))
        >>> print('%s: %s' % (type(t), t))
        >>> print('%s dtype: %s meta: %s' % (type(t.keys), t.keys.dtype, t.keys.meta))
        >>> print('%s dtype: %s meta: %s' % (type(t.values), t.values.dtype, t.values.meta))
        <class 'qpython.qcollection.QKeyedTable'>: [(1001L,) (1002L,) (1003L,)]![('d1', 366) ('d2', 121) ('d3', -2147483648)]
        <class 'qpython.qcollection.QTable'> dtype: [('eid', '<i8')] meta: metadata(qtype=98, eid=-7)
        <class 'qpython.qcollection.QTable'> dtype: [('pos', 'S2'), ('dates', '<i4')] meta: metadata(dates=-14, qtype=98, pos=-11)
    
    :Parameters:
     - `keys` (`QTable`) - table keys
     - `values` (`QTable`) - table values
    
    :raises: `ValueError`
    '''
    def __init__(self, keys, values):
        if not isinstance(keys, QTable):
            raise ValueError('Keys array is required to be of type: QTable')

        if not isinstance(values, QTable):
            raise ValueError('Values array is required to be of type: QTable')

        if len(keys) != len(values):
            raise ValueError('Keys and value arrays cannot have different length')
        self.keys = keys
        self.values = values

    def __str__(self, *args, **kwargs):
        return '%s!%s' % (self.keys, self.values)

    def __eq__(self, other):
        return isinstance(other, QKeyedTable) and numpy.array_equal(self.keys, other.keys) and numpy.array_equal(self.values, other.values)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.keys)

    def __iter__(self):
        return iter(self.keys)

    def items(self):
        '''Return a copy of the keyed table's list of ``(key, value)`` pairs.'''
        return [(self.keys[x], self.values[x]) for x in range(len(self.keys))]

    def iteritems(self):
        '''Return an iterator over the keyed table's ``(key, value)`` pairs.'''
        for x in range(len(self.keys)):
            yield (self.keys[x], self.values[x])

    def iterkeys(self):
        '''Return an iterator over the keyed table's keys.'''
        return iter(self.keys)

    def itervalues(self):
        '''Return an iterator over the keyed table's values.'''
        return iter(self.values)
