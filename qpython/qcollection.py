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

import numpy

from qpython import MetaData
from qpython.qtype import QTABLE, FROM_Q, QSYMBOL


class QList(numpy.ndarray):
    '''Represents a q list.'''
    def meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.dtype, self.meta.qtype, self.tostring()))



def qlist(array, adjust_dtype = True, **meta):
    '''Converts a numpy.array to q vector and enriches object instance with given meta data.'''
    if meta and 'qtype' in meta:
        qtype = -abs(meta['qtype'])
        dtype = FROM_Q[qtype]
        if dtype != array.dtype:
            array = array.astype(dtype = dtype)
    
    vector = array.view(QList)
    vector.meta_init(**meta)
    return vector



class QDictionary(object):
    '''Represents a q dictionary.'''
    def __init__(self, keys, values):
        if not isinstance(keys, (QList, tuple, list)):
            raise ValueError('%s expects keys to be of type: QList, tuple or list. Actual type: %s' % (self.__class__.__name__, type(keys)))
        if not isinstance(values, (QList, tuple, list)):
            raise ValueError('%s expects values to be of type: QList, tuple or list. Actual type: %s' % (self.__class__.__name__, type(values)))

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



class QTable(numpy.recarray):
    '''Represents a q table.'''
    def meta_init(self, **meta):
        self.meta = MetaData(**meta)

    def __eq__(self, other):
        return numpy.array_equal(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)
        
        

def qtable(columns, data, **meta):
    '''Creates a QTable out of given column names and data, and initializes the meta data.'''
    if len(columns) != len(data):
        raise ValueError('Number of columns doesn`t match the data layout. %s vs %s' % (len(columns), len(data)))
    
    if not meta or not 'qtype' in meta:
        meta = {} if not meta else meta
        meta['qtype'] = QTABLE
    
    table = numpy.core.records.fromarrays(data, names = ','.join(columns))
    table = table.view(QTable)
    
    for i in xrange(len(columns)):
        if isinstance(data[i], QList):
            meta[columns[i]] = data[i].meta.qtype
    
    table.meta_init(**meta)
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
    
    def get(self, key, default = None):
        idx = 0
        for k in self.keys:
            if k == key:
                return self.values[idx]
            idx += 1
        return default
    
    def has_key(self, key):
        for k in self.keys:
            if k == key:
                return True
        return False
        
    def __contains__(self, key):
        return self.has_key(key)
    
    def items(self):
        return [(self.keys[x], self.values[x]) for x in xrange(len(self.keys))]
    
    def iteritems(self):
        for x in xrange(len(self.keys)):
            yield (self.keys[x], self.values[x])
            
    def iterkeys(self):
        return iter(self.keys)
    
    def itervalues(self):
        return iter(self.values)