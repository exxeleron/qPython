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
from qtype import *  # @UnusedWildImport


_MILIS_PER_DAY = 24 * 60 * 60 * 1000

_EPOCH_QMONTH = numpy.datetime64('2000-01', 'M')
_EPOCH_QDATE = numpy.datetime64('2000-01-01', 'D')
_EPOCH_QDATETIME = numpy.datetime64('2000-01-01T00:00:00.000', 'ms')
_EPOCH_TIMESTAMP = numpy.datetime64('2000-01-01T00:00:00', 'ns')


_QMONTH_NULL = qnull(QMONTH)
_QDATE_NULL = qnull(QDATE)
_QDATETIME_NULL = qnull(QDATETIME)
_QMINUTE_NULL = qnull(QMINUTE)
_QSECOND_NULL = qnull(QSECOND)
_QTIME_NULL = qnull(QTIME)
_QTIMESTAMP_NULL = qnull(QTIMESTAMP)
_QTIMESPAN_NULL = qnull(QTIMESPAN)



class QTemporal(object):
    '''Represents a q temporal value.'''

    def __init__(self, dt):
        self._datetime = dt

    def meta_init(self, **meta):
        self.meta = MetaData(**meta)

    @property
    def raw(self):
        return self._datetime

    def __str__(self):
        return '%s [%s]' % (self._datetime, self.meta)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self._datetime == other._datetime)

    def __ne__(self, other):
        return not self.__eq__(other)



def qtemporal(dt, **meta):
    '''Converts a numpy.datetime64 to q temporal object and enriches object instance with given meta data.'''
    result = QTemporal(dt)
    result.meta_init(**meta)
    return result



def from_raw_qtemporal(raw, qtype):
    return qtemporal(_FROM_Q[qtype](raw), qtype = qtype)



def to_raw_qtemporal(dt, qtype):
    return _TO_Q[qtype](dt)



def _from_qmonth(raw):
    if raw == _QMONTH_NULL:
        return _QMONTH_NULL
    else:
        return _EPOCH_QMONTH + numpy.timedelta64(int(raw), 'M')



def _to_qmonth(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QMONTH).astype(int)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qdate(raw):
    if raw == _QDATE_NULL:
        return _QDATE_NULL
    else:
        return _EPOCH_QDATE + numpy.timedelta64(int(raw), 'D')



def _to_qdate(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QDATE).astype(int)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qdatetime(raw):
    if numpy.isnan(raw) or raw == _QDATETIME_NULL:
        return _QDATETIME_NULL
    else:
        return _EPOCH_QDATETIME + numpy.timedelta64(long(_MILIS_PER_DAY * raw), 'ms')



def _to_qdatetime(dt):
    t_dt = type(dt)
    if t_dt == numpy.float64:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_QDATETIME).astype(float) / _MILIS_PER_DAY
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qminute(raw):
    if raw == _QMINUTE_NULL:
        return _QMINUTE_NULL
    else:
        return numpy.timedelta64(int(raw), 'm')



def _to_qminute(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qsecond(raw):
    if raw == _QSECOND_NULL:
        return _QSECOND_NULL
    else:
        return numpy.timedelta64(int(raw), 's')



def _to_qsecond(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtime(raw):
    if raw == _QTIME_NULL:
        return _QTIME_NULL
    else:
        return numpy.timedelta64(int(raw), 'ms')



def _to_qtime(dt):
    t_dt = type(dt)
    if t_dt == numpy.int32:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(int)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtimestamp(raw):
    if raw == _QTIMESTAMP_NULL:
        return _QTIMESTAMP_NULL
    else:
        return _EPOCH_TIMESTAMP + numpy.timedelta64(long(raw), 'ns')



def _to_qtimestamp(dt):
    t_dt = type(dt)
    if t_dt == numpy.int64:
        return dt
    elif t_dt == numpy.datetime64:
        return (dt - _EPOCH_TIMESTAMP).astype(long)
    else:
        raise ValueError('Cannot convert %s of type %s to q value.' % (dt, type(dt)))



def _from_qtimespan(raw):
    if raw == _QTIMESPAN_NULL:
        return _QTIMESPAN_NULL
    else:
        return numpy.timedelta64(long(raw), 'ns')



def _to_qtimespan(dt):
    t_dt = type(dt)
    if t_dt == numpy.int64:
        return dt
    elif t_dt == numpy.timedelta64:
        return dt.astype(long)
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
