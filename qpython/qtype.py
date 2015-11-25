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

'''
The `qpython.qtype` module defines number of utility function which help to work
with types mapping between q and Python.

This module declares supported q types as constants, which can be used along
with conversion functions e.g.: :func:`.qcollection.qlist` or 
:func:`.qtemporal.qtemporal`. 

List of q type codes:

==================     =============
q type name             q type code
==================     =============
QNULL                  0x65
QGENERAL_LIST          0x00
QBOOL                  -0x01
QBOOL_LIST             0x01
QGUID                  -0x02
QGUID_LIST             0x02
QBYTE                  -0x04
QBYTE_LIST             0x04
QSHORT                 -0x05
QSHORT_LIST            0x05
QINT                   -0x06
QINT_LIST              0x06
QLONG                  -0x07
QLONG_LIST             0x07
QFLOAT                 -0x08
QFLOAT_LIST            0x08
QDOUBLE                -0x09
QDOUBLE_LIST           0x09
QCHAR                  -0x0a
QSTRING                0x0a
QSTRING_LIST           0x00
QSYMBOL                -0x0b
QSYMBOL_LIST           0x0b
QTIMESTAMP             -0x0c
QTIMESTAMP_LIST        0x0c
QMONTH                 -0x0d
QMONTH_LIST            0x0d
QDATE                  -0x0e
QDATE_LIST             0x0e
QDATETIME              -0x0f
QDATETIME_LIST         0x0f
QTIMESPAN              -0x10
QTIMESPAN_LIST         0x10
QMINUTE                -0x11
QMINUTE_LIST           0x11
QSECOND                -0x12
QSECOND_LIST           0x12
QTIME                  -0x13
QTIME_LIST             0x13
QDICTIONARY            0x63
QKEYED_TABLE           0x63
QTABLE                 0x62
QLAMBDA                0x64
QUNARY_FUNC            0x65
QBINARY_FUNC           0x66
QTERNARY_FUNC          0x67
QCOMPOSITION_FUNC      0x69
QADVERB_FUNC_106       0x6a
QADVERB_FUNC_107       0x6b
QADVERB_FUNC_108       0x6c
QADVERB_FUNC_109       0x6d
QADVERB_FUNC_110       0x6e
QADVERB_FUNC_111       0x6f
QPROJECTION            0x68
QERROR                 -0x80
==================     =============
'''

import numpy
import re
import uuid
import sys
from functools import reduce
if sys.version > '3':
    long = int

# qtype constants:
QNULL               =  0x65
QGENERAL_LIST       =  0x00
QBOOL               =  -0x01
QBOOL_LIST          =  0x01
QGUID               =  -0x02
QGUID_LIST          =  0x02
QBYTE               =  -0x04
QBYTE_LIST          =  0x04
QSHORT              =  -0x05
QSHORT_LIST         =  0x05
QINT                =  -0x06
QINT_LIST           =  0x06
QLONG               =  -0x07
QLONG_LIST          =  0x07
QFLOAT              =  -0x08
QFLOAT_LIST         =  0x08
QDOUBLE             =  -0x09
QDOUBLE_LIST        =  0x09
QCHAR               =  -0x0a
QSTRING             =  0x0a
QSTRING_LIST        =  0x00
QSYMBOL             =  -0x0b
QSYMBOL_LIST        =  0x0b

QTIMESTAMP          =  -0x0c
QTIMESTAMP_LIST     =  0x0c
QMONTH              =  -0x0d
QMONTH_LIST         =  0x0d
QDATE               =  -0x0e
QDATE_LIST          =  0x0e
QDATETIME           =  -0x0f
QDATETIME_LIST      =  0x0f
QTIMESPAN           =  -0x10
QTIMESPAN_LIST      =  0x10
QMINUTE             =  -0x11
QMINUTE_LIST        =  0x11
QSECOND             =  -0x12
QSECOND_LIST        =  0x12
QTIME               =  -0x13
QTIME_LIST          =  0x13

QDICTIONARY         =  0x63
QKEYED_TABLE        =  0x63
QTABLE              =  0x62
QLAMBDA             =  0x64
QUNARY_FUNC         =  0x65
QBINARY_FUNC        =  0x66
QTERNARY_FUNC       =  0x67
QCOMPOSITION_FUNC   =  0x69
QADVERB_FUNC_106    =  0x6a
QADVERB_FUNC_107    =  0x6b
QADVERB_FUNC_108    =  0x6c
QADVERB_FUNC_109    =  0x6d
QADVERB_FUNC_110    =  0x6e
QADVERB_FUNC_111    =  0x6f
QPROJECTION         =  0x68

QERROR              = -0x80



ATOM_SIZE = ( 0, 1, 16, 0, 1, 2, 4, 8, 4, 8, 1, 0, 8, 4, 4, 8, 8, 4, 4, 4 )



# mapping of q atoms to corresponding Python types
PY_TYPE = {
    QBOOL:          numpy.bool_,
    QBYTE:          numpy.byte,
    QGUID:          numpy.object_,
    QSHORT:         numpy.int16,
    QINT:           numpy.int32,
    QLONG:          numpy.int64,
    QFLOAT:         numpy.float32,
    QDOUBLE:        numpy.float64,
    QCHAR:          numpy.byte,
    QSYMBOL:        numpy.string_,
    QMONTH:         numpy.int32,
    QDATE:          numpy.int32,
    QDATETIME:      numpy.float64,
    QMINUTE:        numpy.int32,
    QSECOND:        numpy.int32,
    QTIME:          numpy.int32,
    QTIMESTAMP:     numpy.int64,
    QTIMESPAN:      numpy.int64,
    # artificial qtype for convenient conversion of string lists
    QSTRING_LIST:   numpy.object_,
    }


# mapping of Python types to corresponding q atoms
Q_TYPE = {
    bool             : QBOOL,
    numpy.bool       : QBOOL,
    numpy.bool_      : QBOOL,
    numpy.byte       : QBYTE,
    numpy.int16      : QSHORT,
    int              : QINT,
    numpy.int32      : QINT,
    long             : QLONG,
    numpy.int64      : QLONG,
    numpy.float32    : QFLOAT,
    float            : QDOUBLE,
    numpy.float64    : QDOUBLE,
    str              : QSTRING,
    bytes            : QSTRING,
    numpy.string_    : QSYMBOL,
    uuid.UUID        : QGUID,
    }


# mapping of numpy datetime64/timedelta64 to q temporal types
TEMPORAL_PY_TYPE = {
    'datetime64[M]'    : QMONTH,
    'datetime64[D]'    : QDATE,
    'datetime64[ms]'   : QDATETIME,
    'timedelta64[m]'   : QMINUTE,
    'timedelta64[s]'   : QSECOND,
    'timedelta64[ms]'  : QTIME,
    'datetime64[ns]'   : QTIMESTAMP,
    'timedelta64[ns]'  : QTIMESPAN
    }


TEMPORAL_Q_TYPE = {
    QMONTH:      'datetime64[M]',
    QDATE:       'datetime64[D]',
    QDATETIME:   'datetime64[ms]',
    QMINUTE:     'timedelta64[m]',
    QSECOND:     'timedelta64[s]',
    QTIME:       'timedelta64[ms]',
    QTIMESTAMP:  'datetime64[ns]',
    QTIMESPAN:   'timedelta64[ns]'
    }


# mapping of q types for Python binary translation
STRUCT_MAP = {
    QBOOL:      'b',
    QBYTE:      'b',
    QSHORT:     'h',
    QINT:       'i',
    QLONG:      'q',
    QFLOAT:     'f',
    QDOUBLE:    'd',
    QSTRING:    's',
    QSYMBOL:    'S',
    QCHAR:      'b',

    QMONTH:     'i',
    QDATE:      'i',
    QDATETIME:  'd',
    QMINUTE:    'i',
    QSECOND:    'i',
    QTIME:      'i',
    QTIMESPAN:  'q',
    QTIMESTAMP: 'q',
    }


# null definitions
_QNULL1 = numpy.int8(-2**7)
_QNULL2 = numpy.int16(-2**15)
_QNULL4 = numpy.int32(-2**31)
_QNULL8 = numpy.int64(-2**63)
_QNAN32 = numpy.fromstring(b'\x00\x00\xc0\x7f', dtype=numpy.float32)[0]
_QNAN64 = numpy.fromstring(b'\x00\x00\x00\x00\x00\x00\xf8\x7f', dtype=numpy.float64)[0]
_QNULL_BOOL = numpy.bool_(False)
_QNULL_SYM = numpy.string_('')
_QNULL_GUID = uuid.UUID('00000000-0000-0000-0000-000000000000')


QNULLMAP = {
    QGUID:       ('0Ng',    _QNULL_GUID,         lambda v: v == _QNULL_GUID),
    QBOOL:       ('0b',     _QNULL_BOOL,         lambda v: v == numpy.bool_(False)),
    QBYTE:       ('0x00',   _QNULL1,             lambda v: v == _QNULL1),
    QSHORT:      ('0Nh',    _QNULL2,             lambda v: v == _QNULL2),
    QINT:        ('0N',     _QNULL4,             lambda v: v == _QNULL4),
    QLONG:       ('0Nj',    _QNULL8,             lambda v: v == _QNULL8),
    QFLOAT:      ('0Ne',    _QNAN32,             lambda v: numpy.isnan(v)),
    QDOUBLE:     ('0n',     _QNAN64,             lambda v: numpy.isnan(v)),
    QSTRING:     ('" "',    b' ',                 lambda v: v == b' '),
    QSYMBOL:     ('`',      _QNULL_SYM,          lambda v: v == _QNULL_SYM),
    QMONTH:      ('0Nm',    _QNULL4,             lambda v: v == _QNULL4),
    QDATE:       ('0Nd',    _QNULL4,             lambda v: v == _QNULL4),
    QDATETIME:   ('0Nz',    _QNAN64,             lambda v: numpy.isnan(v)),
    QMINUTE:     ('0Nu',    _QNULL4,             lambda v: v == _QNULL4),
    QSECOND:     ('0Nv',    _QNULL4,             lambda v: v == _QNULL4),
    QTIME:       ('0Nt',    _QNULL4,             lambda v: v == _QNULL4),
    QTIMESPAN:   ('0Nn',    _QNULL8,             lambda v: v == _QNULL8),
    QTIMESTAMP:  ('0Np',    _QNULL8,             lambda v: v == _QNULL8),
    }



def qnull(qtype):
    '''Retrieve null value for requested q type.

    :Parameters:
     - `qtype` (`integer`) - qtype indicator

    :returns: null value for specified q type
    '''
    return QNULLMAP[qtype][1]



def is_null(value, qtype):
    '''Checks whether given value matches null value for a particular q type.

    :Parameters:
     - `qtype` (`integer`) - qtype indicator

    :returns: `boolean` - ``True`` if value is considered null for given type
              ``False`` otherwise
    '''
    return QNULLMAP[qtype][2](value)



class QException(Exception):
    '''Represents a q error.'''
    pass



class QFunction(object):
    '''Represents a q function.'''

    def __init__(self, qtype):
        self.qtype = qtype


    def __str__(self):
        return '%s#%s' % (self.__class__.__name__, self.qtype)



class QLambda(QFunction):

    '''Represents a q lambda expression.

    .. note:: `expression` is trimmed and required to be valid q function 
              (``{..}``) or k function (``k){..}``).

    :Parameters:
     - `expression` (`string`) - lambda expression

    :raises: `ValueError`
    '''
    def __init__(self, expression):
        QFunction.__init__(self, QLAMBDA)

        if not expression:
            raise ValueError('Lambda expression cannot be None or empty')

        expression = expression.strip()

        if not QLambda._EXPRESSION_REGEX.match(expression):
            raise ValueError('Invalid lambda expression: %s' % expression)

        self.expression = expression


    _EXPRESSION_REGEX = re.compile(r'\s*(k\))?\s*\{.*\}')


    def __str__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.expression)


    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.expression == other.expression)



class QProjection(QFunction):

    '''Represents a q projection.

    :Parameters:
     - `parameters` (`list`) - list of parameters for lambda expression
    '''
    def __init__(self, parameters):
        QFunction.__init__(self, QPROJECTION)

        self.parameters = parameters


    def __str__(self):
        parameters_str = []
        for arg in self.parameters:
            parameters_str.append('%s' % arg)

        return '%s(%s)' % (self.__class__.__name__, ', '.join(parameters_str))


    def __eq__(self, other):
        return (not self.parameters and not other.parameters) or \
                reduce(lambda v1,v2: v1 or v2, map(lambda v: v in self.parameters, other.parameters))


    def __ne__(self, other):
        return not self.__eq__(other)



class Mapper(object):
    '''Utility class for creating function execution map via decorators.

    :Parameters:
     - `call_map` (`dictionary`) -  target execution map
    '''
    def __init__(self, call_map):
        self.call_map = call_map


    def __call__(self, *args):
        def wrap(func):
            for arg in args:
                self.call_map[arg] = func
            return func
        return wrap
