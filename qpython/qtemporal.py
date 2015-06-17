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

from qpython import MetaData
from qpython.qtype import *  # @UnusedWildImport
from numpy import longlong

_MILLIS_PER_DAY = 24 * 60 * 60 * 1000
_MILLIS_PER_DAY_FLOAT = float(_MILLIS_PER_DAY)
_QEPOCH_MS = long(10957 * _MILLIS_PER_DAY)
_EPOCH_QTIMESTAMP_NS = _QEPOCH_MS * 1000000


_EPOCH_QMONTH = numpy.datetime64('2000-01', 'M')
_EPOCH_QDATE = numpy.datetime64('2000-01-01', 'D')
_EPOCH_QDATETIME = numpy.datetime64(_QEPOCH_MS, 'ms')
_EPOCH_TIMESTAMP = numpy.datetime64(_EPOCH_QTIMESTAMP_NS, 'ns')


_QMONTH_NULL = qnull(QMONTH)
_QDATE_NULL = qnull(QDATE)
_QDATETIME_NULL = qnull(QDATETIME)
_QMINUTE_NULL = qnull(QMINUTE)
_QSECOND_NULL = qnull(QSECOND)
_QTIME_NULL = qnull(QTIME)
_QTIMESTAMP_NULL = qnull(QTIMESTAMP)
_QTIMESPAN_NULL = qnull(QTIMESPAN)



class QTemporal(object):
    '''
    Represents a q temporal value.
    
    The :class:`.QTemporal` wraps `numpy.datetime64` or `numpy.timedelta64`
    along with meta-information like qtype indicator.
    
    :Parameters:
     - `dt` (`numpy.datetime64` or `numpy.timedelta64`) - datetime to be wrapped
    '''

    def __init__(self, dt):
        self._datetime = dt

    def _meta_init(self, **meta):
        self.meta = MetaData(**meta)

    @property
    def raw(self):
        '''Return wrapped datetime object.
        
        :returns: `numpy.datetime64` or `numpy.timedelta64` - wrapped datetime
        '''
        return self._datetime

    def __str__(self):
        return '%s [%s]' % (self._datetime, self.meta)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.meta.qtype == other.meta.qtype
            and self._datetime == other._datetime)

    def __ne__(self, other):
        return not self.__eq__(other)



def qtemporal(dt, **meta):
    '''Converts a `numpy.datetime64` or `numpy.timedelta64` to 
    :class:`.QTemporal` and enriches object instance with given meta data.
    
    Examples:
    
       >>> qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE)
       2001-01-01 [metadata(qtype=-14)]
       >>> qtemporal(numpy.timedelta64(43499123, 'ms'), qtype=QTIME)
       43499123 milliseconds [metadata(qtype=-19)]
       >>> qtemporal(qnull(QDATETIME), qtype=QDATETIME)
       nan [metadata(qtype=-15)]
    
    :Parameters:
     - `dt` (`numpy.datetime64` or `numpy.timedelta64`) - datetime to be wrapped
    :Kwargs:
     - `qtype` (`integer`) - qtype indicator
    
    :returns: `QTemporal` - wrapped datetime 
    '''
    result = QTemporal(dt)
    result._meta_init(**meta)
    return result



def from_raw_qtemporal(raw, qtype):
    '''
    Converts raw numeric value to `numpy.datetime64` or `numpy.timedelta64`
    instance.
    
    Actual conversion applied to raw numeric value depends on `qtype` parameter.
    
    :Parameters:
     - `raw` (`integer`, `float`) - raw representation to be converted
     - `qtype` (`integer`) - qtype indicator
     
    :returns: `numpy.datetime64` or `numpy.timedelta64` - converted datetime
    '''
    return _FROM_Q[qtype](raw)



def to_raw_qtemporal(dt, qtype):
    '''
    Converts datetime/timedelta instance to raw numeric value.
    
    Actual conversion applied to datetime/timedelta instance depends on `qtype` 
    parameter.
    
    :Parameters:
     - `dt` (`numpy.datetime64` or `numpy.timedelta64`) - datetime/timedelta
       object to be converted
     - `qtype` (`integer`) - qtype indicator
     
    :returns: `integer`, `float` - raw numeric value
    '''
    return _TO_Q[qtype](dt)



def array_from_raw_qtemporal(raw, qtype):
    '''
    Converts `numpy.array` containing raw q representation to ``datetime64``/``timedelta64``
    array.
    
    Examples:
    
      >>> raw = numpy.array([366, 121, qnull(QDATE)])
      >>> print(array_from_raw_qtemporal(raw, qtype = QDATE))
      ['2001-01-01' '2000-05-01' 'NaT']
    
    :Parameters:
     - `raw` (`numpy.array`) - numpy raw array to be converted
     - `qtype` (`integer`) - qtype indicator
    
    :returns: `numpy.array` - numpy array with ``datetime64``/``timedelta64``
    
    :raises: `ValueError`
    '''
    if not isinstance(raw, numpy.ndarray):
        raise ValueError('raw parameter is expected to be of type: numpy.ndarray. Was: %s' % type(raw))

    qtype = -abs(qtype)
    conversion = _FROM_RAW_LIST[qtype]

    mask = raw == qnull(qtype)

    dtype = PY_TYPE[qtype]
    array = raw.astype(dtype) if dtype != raw.dtype else raw

    array = conversion(array) if conversion else array
    null = _NUMPY_NULL[qtype]
    array = numpy.where(mask, null, array)
    return array



def array_to_raw_qtemporal(array, qtype):
    '''
    Converts `numpy.array` containing ``datetime64``/``timedelta64`` to raw
    q representation.
    
    Examples:
    
      >>> na_dt = numpy.arange('1999-01-01', '2005-12-31', dtype='datetime64[D]')
      >>> print(array_to_raw_qtemporal(na_dt, qtype = QDATE_LIST))
      [-365 -364 -363 ..., 2188 2189 2190]
      >>> array_to_raw_qtemporal(numpy.arange(-20, 30, dtype='int32'), qtype = QDATE_LIST)
      Traceback (most recent call last):
        ...
      ValueError: array.dtype is expected to be of type: datetime64 or timedelta64. Was: int32
    
    :Parameters:
     - `array` (`numpy.array`) - numpy datetime/timedelta array to be converted
     - `qtype` (`integer`) - qtype indicator
    
    :returns: `numpy.array` - numpy array with raw values
    
    :raises: `ValueError`
    '''
    if not isinstance(array, numpy.ndarray):
        raise ValueError('array parameter is expected to be of type: numpy.ndarray. Was: %s' % type(array))

    if not array.dtype.type in (numpy.datetime64, numpy.timedelta64):
        raise ValueError('array.dtype is expected to be of type: datetime64 or timedelta64. Was: %s' % array.dtype)

    qtype = -abs(qtype)
    conversion = _TO_RAW_LIST[qtype]
    raw = array.view(numpy.int64).view(numpy.ndarray)
    mask = raw == numpy.int64(-2 ** 63)

    raw = conversion(raw) if conversion else raw
    null = qnull(qtype)
    raw = numpy.where(mask, null, raw)
    return raw



def _from_qmonth(raw):
    if raw == _QMONTH_NULL:
        return _NUMPY_NULL[QMONTH]
    else:
        return _EPOCH_QMONTH + numpy.timedelta64(int(raw), 'M')



def _to_qmonth(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QMONTH).astype(int) if not dt == _NUMPY_NULL[QMONTH] else _QMONTH_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qdate(raw):
    if raw == _QDATE_NULL:
        return _NUMPY_NULL[QDATE]
    else:
        return _EPOCH_QDATE + numpy.timedelta64(int(raw), 'D')



def _to_qdate(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QDATE).astype(int) if not dt == _NUMPY_NULL[QDATE] else _QDATE_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qdatetime(raw):
    if numpy.isnan(raw) or raw == _QDATETIME_NULL:
        return _NUMPY_NULL[QDATETIME]
    else:
        return _EPOCH_QDATETIME + numpy.timedelta64(long(_MILLIS_PER_DAY * raw), 'ms')



def _to_qdatetime(dt):
    t_dt = type(dt)
    if t_dt == numpy.float64:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QDATETIME).astype(float) / _MILLIS_PER_DAY if not dt == _NUMPY_NULL[QDATETIME] else _QDATETIME_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qminute(raw):
    if raw == _QMINUTE_NULL:
        return _NUMPY_NULL[QMINUTE]
    else:
        return numpy.timedelta64(int(raw), 'm')



def _to_qminute(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int) if not dt == _NUMPY_NULL[QMINUTE] else _QMINUTE_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qsecond(raw):
    if raw == _QSECOND_NULL:
        return _NUMPY_NULL[QSECOND]
    else:
        return numpy.timedelta64(int(raw), 's')



def _to_qsecond(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int) if not dt == _NUMPY_NULL[QSECOND] else _QSECOND_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtime(raw):
    if raw == _QTIME_NULL:
        return _NUMPY_NULL[QTIME]
    else:
        return numpy.timedelta64(int(raw), 'ms')



def _to_qtime(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int) if not dt == _NUMPY_NULL[QTIME] else _QTIME_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtimestamp(raw):
    if raw == _QTIMESTAMP_NULL:
        return _NUMPY_NULL[QTIMESTAMP]
    else:
        return _EPOCH_TIMESTAMP + numpy.timedelta64(long(raw), 'ns')



def _to_qtimestamp(dt):
    t_dt = type(dt)
    if t_dt == numpy.int64:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_TIMESTAMP).astype(longlong) if not dt == _NUMPY_NULL[QTIMESTAMP] else _QTIMESTAMP_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtimespan(raw):
    if raw == _QTIMESPAN_NULL:
        return _NUMPY_NULL[QTIMESPAN]
    else:
        return numpy.timedelta64(long(raw), 'ns')



def _to_qtimespan(dt):
    t_dt = type(dt)
    if t_dt == numpy.int64:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(longlong) if not dt == _NUMPY_NULL[QTIMESPAN] else _QTIMESTAMP_NULL
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



_FROM_Q = {
           QMONTH:          _from_qmonth,
           QDATE:           _from_qdate,
           QDATETIME:       _from_qdatetime,
           QMINUTE:         _from_qminute,
           QSECOND:         _from_qsecond,
           QTIME:           _from_qtime,
           QTIMESTAMP:      _from_qtimestamp,
           QTIMESPAN:       _from_qtimespan,
           }



_TO_Q = {
         QMONTH:            _to_qmonth,
         QDATE:             _to_qdate,
         QDATETIME:         _to_qdatetime,
         QMINUTE:           _to_qminute,
         QSECOND:           _to_qsecond,
         QTIME:             _to_qtime,
         QTIMESTAMP:        _to_qtimestamp,
         QTIMESPAN:         _to_qtimespan,
         }


_TO_RAW_LIST = {
                QMONTH:      lambda a: (a - 360).astype(numpy.int32),
                QDATE:       lambda a: (a - 10957).astype(numpy.int32),
                QDATETIME:   lambda a: ((a - _QEPOCH_MS) / _MILLIS_PER_DAY_FLOAT).astype(numpy.float64),
                QMINUTE:     lambda a: a.astype(numpy.int32),
                QSECOND:     lambda a: a.astype(numpy.int32),
                QTIME:       lambda a: a.astype(numpy.int32),
                QTIMESTAMP:  lambda a: a - _EPOCH_QTIMESTAMP_NS,
                QTIMESPAN:   None,
                }



_FROM_RAW_LIST = {
                  QMONTH:      lambda a: numpy.array((a + 360), dtype = 'datetime64[M]'),
                  QDATE:       lambda a: numpy.array((a + 10957), dtype = 'datetime64[D]'),
                  QDATETIME:   lambda a: numpy.array((a * _MILLIS_PER_DAY + _QEPOCH_MS), dtype = 'datetime64[ms]'),
                  QMINUTE:     lambda a: numpy.array(a, dtype = 'timedelta64[m]'),
                  QSECOND:     lambda a: numpy.array(a, dtype = 'timedelta64[s]'),
                  QTIME:       lambda a: numpy.array(a, dtype = 'timedelta64[ms]'),
                  QTIMESTAMP:  lambda a: numpy.array((a + _EPOCH_QTIMESTAMP_NS), dtype = 'datetime64[ns]'),
                  QTIMESPAN:   lambda a: numpy.array(a, dtype = 'timedelta64[ns]'),
                  }



_NUMPY_NULL = {
               QMONTH:      numpy.datetime64('NaT', 'M'),
               QDATE:       numpy.datetime64('NaT', 'D'),
               QDATETIME:   numpy.datetime64('NaT', 'ms'),
               QMINUTE:     numpy.timedelta64('NaT', 'm'),
               QSECOND:     numpy.timedelta64('NaT', 's'),
               QTIME:       numpy.timedelta64('NaT', 'ms'),
               QTIMESTAMP:  numpy.datetime64('NaT', 'ns'),
               QTIMESPAN:   numpy.timedelta64('NaT', 'ns'),
               }
