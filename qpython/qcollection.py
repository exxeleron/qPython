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

from qtype import *  # @UnusedWildImport
from qpython import MetaData
from qpython.qtemporal import from_raw_qtemporal, to_raw_qtemporal


class QList(numpy.ndarray):
    '''Represents a q list.'''
    def _meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.dtype, self.meta.qtype, self.tostring()))



class QTemporalList(QList):
    '''Represents a q list of datetime objects.'''
    def _meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __getitem__(self, idx):
        return from_raw_qtemporal(numpy.ndarray.__getitem__(self, idx), -abs(self.meta.qtype))

    def __setitem__(self, idx, value):
        numpy.ndarray.__setitem__(self, idx, to_raw_qtemporal(value, --abs(self.meta.qtype)))

    def raw(self, idx):
        return numpy.ndarray.__getitem__(self, idx)



def get_list_qtype(array):
    '''Guesses a corresponding qtype based on provided QList/numpy.ndarray instance.'''
    if not isinstance(array, numpy.ndarray):
        raise ValueError('array parameter is expected to be of type: numpy.ndarray, got: %s' % type(array))
    
    if isinstance(array, QList):
        return -abs(array.meta.qtype)

    qtype = None
    
    if array.dtype == '|S1':
        qtype = QCHAR

    if qtype is None:
        qtype = Q_TYPE.get(array.dtype.type, None)

    if qtype is None:
        # determinate type based on first element of the numpy array
        qtype = Q_TYPE.get(type(array[0]), QGENERAL_LIST)
        
    return qtype



def qlist(array, **meta):
    '''Converts an input array to q vector and enriches object instance with given meta data. If necessary input array is converted from tuple or list to numpy.array.'''
    if type(array) in (list, tuple):
        array = numpy.array(array)
    
    if not isinstance(array, numpy.ndarray):
        raise ValueError('array parameter is expected to be of type: numpy.ndarray, list or tuple. Was: %s' % type(array))

    qtype = None
        
    if meta and 'qtype' in meta:
        qtype = -abs(meta['qtype'])
        dtype = PY_TYPE[qtype]
        if dtype != array.dtype:
            array = array.astype(dtype = dtype)

    qtype = get_list_qtype(array) if qtype is None else qtype
    meta['qtype'] = qtype

    vector = array.view(QList) if not -abs(meta['qtype']) in [QMONTH, QDATE, QDATETIME, QMINUTE, QSECOND, QTIME, QTIMESTAMP, QTIMESPAN] else array.view(QTemporalList)
    vector._meta_init(**meta)
    return vector



class QDictionary(object):
    '''Represents a q dictionary.'''
    def __init__(self, keys, values):
        if not isinstance(keys, (QList, tuple, list)):
            raise ValueError('%s expects keys to be of type: QList, tuple or list. Actual type: %s' % (self.__class__.__name__, type(keys)))
        if not isinstance(values, (QTable, QList, tuple, list)):
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
        return [(self.keys[x], self.values[x]) for x in xrange(len(self.keys))]

    def iteritems(self):
        for x in xrange(len(self.keys)):
            yield (self.keys[x], self.values[x])

    def iterkeys(self):
        return iter(self.keys)

    def itervalues(self):
        return iter(self.values)



class QTable(numpy.recarray):
    '''Represents a q table.'''
    def _meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)



def qtable(columns, data, **meta):
    '''Creates a QTable out of given column names and data, and initializes the meta data.'''
    if len(columns) != len(data):
        raise ValueError('Number of columns doesn`t match the data layout. %s vs %s' % (len(columns), len(data)))

    meta = {} if not meta else meta
    
    if not 'qtype' in meta:
        meta['qtype'] = QTABLE
        
    for i in xrange(len(columns)):
        if isinstance(data[i], str):
            # convert character list (represented as string) to numpy representation
            data[i] = numpy.array(list(data[i]), dtype = numpy.str)
         
        if columns[i] in meta:
            data[i] = qlist(data[i], qtype = meta[columns[i]])
        else:
            data[i] = qlist(data[i])
        
        meta[columns[i]] = data[i].meta.qtype

    table = numpy.core.records.fromarrays(data, names = ','.join(columns))
    table = table.view(QTable)

    table._meta_init(**meta)
    return table



class QKeyedTable(object):
    '''Represents a q keyed table.'''
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
        return [(self.keys[x], self.values[x]) for x in xrange(len(self.keys))]

    def iteritems(self):
        for x in xrange(len(self.keys)):
            yield (self.keys[x], self.values[x])

    def iterkeys(self):
        return iter(self.keys)

    def itervalues(self):
        return iter(self.values)
