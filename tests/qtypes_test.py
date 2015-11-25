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

import pytest
import sys

if sys.version > '3':
    long = int

from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import *  # @UnusedWildImport
from qpython.qtemporal import * # @UnusedWildImport
from qpython.qtemporal import _MILLIS_PER_DAY


def test_is_null():
    assert is_null(qnull(QSYMBOL), QSYMBOL)
    assert is_null(numpy.string_(''), QSYMBOL)
    assert is_null(b'', QSYMBOL)
    assert not is_null(b' ', QSYMBOL)
    assert not is_null(numpy.string_(' '), QSYMBOL)

    assert is_null(qnull(QSTRING), QSTRING)
    assert is_null(b' ', QSTRING)
    assert not is_null(b'', QSTRING)
    assert not is_null(numpy.string_(''), QSTRING)
    assert is_null(numpy.string_(' '), QSTRING)

    assert is_null(qnull(QBOOL), QBOOL)
    assert is_null(numpy.bool_(False), QBOOL)
    assert not is_null(numpy.bool_(True), QBOOL)     

    for t in QNULLMAP.keys():
        assert is_null(qnull(t), t)



def test_qdict():
    with pytest.raises(ValueError):
        QDictionary(qlist(numpy.array([1, 2, 3]), qtype=QLONG_LIST), qlist(numpy.array(['abc', 'cdefgh']), qtype=QSYMBOL_LIST))

    d = QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
                    qlist(numpy.array(['abc', 'cdefgh']), qtype=QSYMBOL_LIST))

    assert len(d) == 2

    assert d[1] == b'abc'
    with pytest.raises(KeyError):
        d['abc']

    assert numpy.int64(1) in d
    assert not -1 in d

    i = 0
    for k in d:
        assert k == d.keys[i]
        assert d[k] == d.values[i]
        i += 1

    i = 0
    for kv in d.iteritems():
        assert kv == (d.keys[i], d.values[i])
        i += 1

    i = 0
    for kv in d.items():
        assert kv == (d.keys[i], d.values[i])
        i += 1

    i = 0
    for k in d.iterkeys():
        assert k == d.keys[i]
        assert d[k] == d.values[i]
        i += 1

    i = 0
    for v in d.itervalues():
        assert v == d.values[i]
        i += 1


def test_qtable():
    with pytest.raises(ValueError):
        qtable(qlist(['name', 'iq'], qtype=QSYMBOL_LIST),
               [qlist([], qtype=QSYMBOL_LIST)])

    with pytest.raises(ValueError):
        qtable(['name', 'iq'],
               [['Beeblebrox', 'Prefect'],
                [98, 42, 126]],
               name=QSYMBOL, iq=QLONG)

    t = qtable(['name', 'iq'],
               [['Dent', 'Beeblebrox', 'Prefect'],
                [98, 42, 126]],
               name=QSYMBOL, iq=QLONG)

    assert len(t) == 3
    assert t[t['name'] == 'Dent']['name'] == b'Dent'
    assert t[t['name'] == 'Dent']['iq'] == long(98)



def test_qkeyedtable():
    with pytest.raises(ValueError):
        QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype=QSYMBOL_LIST),
                           [qlist(numpy.array([1001, 1002, 1003]), qtype=QLONG_LIST)]),
                    ())

    with pytest.raises(ValueError):
        QKeyedTable((),
                    qtable(qlist(numpy.array(['pos', 'dates']), qtype=QSYMBOL_LIST),
                           [qlist(numpy.array(['d1', 'd2', 'd3']), qtype=QSYMBOL_LIST),
                            qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)]))

    t = QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype=QSYMBOL_LIST),
                           [qlist(numpy.array([1001, 1002, 1003]), qtype=QLONG_LIST)]),
                    qtable(qlist(numpy.array(['pos', 'dates']), qtype=QSYMBOL_LIST),
                           [qlist(numpy.array(['d1', 'd2', 'd3']), qtype=QSYMBOL_LIST),
                            qlist(numpy.array([366, 121, 255]), qtype=QINT_LIST)]))

    assert len(t) == 3

    assert t.keys[t.keys['eid'] == 1002]['eid'] == long(1002)
    assert t.values[t.keys['eid'] == 1002]['pos'][0] == b'd2'
    assert t.values[t.keys['eid'] == 1002]['dates'][0] == 121

    i = 0
    for k in t:
        assert k == t.keys[i]
        i += 1

    i = 0
    for kv in t.iteritems():
        assert kv == (t.keys[i], t.values[i])
        i += 1

    i = 0
    for kv in t.items():
        assert kv == (t.keys[i], t.values[i])
        i += 1

    i = 0
    for k in t.iterkeys():
        assert k == t.keys[i]
        i += 1

    i = 0
    for v in t.itervalues():
        assert v == t.values[i]
        i += 1



def test_qtemporallist():
    na_dt = numpy.arange('1999-01-01', '2005-12-31', dtype='datetime64[D]')
    na = array_to_raw_qtemporal(na_dt, qtype=QDATE_LIST)
    t = qlist(na, qtype=QDATE_LIST)

    assert t.meta.qtype == -abs(QDATE_LIST)

    for x in range(len(na)):
        assert t.raw(x) == x - 365
        assert t[x].raw == na_dt[x]
        x += 1


def test_array_to_raw_qtemporal():
    na_dt = numpy.arange('1999-01', '2005-12', dtype='datetime64[M]')
    na = array_to_raw_qtemporal(na_dt, qtype=QMONTH_LIST)
    assert na.dtype == numpy.int32

    for x in range(len(na)):
        assert na[x] == x - 12
        x += 1

    na_dt = numpy.arange('1999-01-01', '2005-12-31', dtype='datetime64[D]')
    na = array_to_raw_qtemporal(na_dt, qtype=QDATE_LIST)
    assert na.dtype == numpy.int32

    for x in range(len(na)):
        assert na[x] == x - 365
        x += 1

    na_dt = numpy.arange('1999-01-01T00:00:00.000Z', '2001-01-04T05:36:57.600Z', 12345678, dtype='datetime64[ms]')
    na = array_to_raw_qtemporal(na_dt, qtype=QDATETIME_LIST)
    assert na.dtype == numpy.float64

    step = 12346678. / _MILLIS_PER_DAY

    assert na[0] == -365.0
    assert abs(na[-1] - 369.1677) < 0.001

    for x in range(len(na)):
        ref = (x * step) - 365
        assert abs(na[x] - ref) < 0.1, '%s %s' %(na[x], ref)

    na_dt = numpy.arange('1999-01-01T00:00:00.000Z', '2001-01-04T05:36:57.600Z', 1234567890000, dtype='datetime64[ns]')
    na = array_to_raw_qtemporal(na_dt, qtype=QTIMESTAMP_LIST)
    assert na.dtype == numpy.int64

    ref = long(-31536000000000000)
    for x in range(len(na)):
        assert na[x] == ref
        ref += long(1234567890000)

    na_dt = numpy.arange(-1000000, 1000000, 12345, dtype='timedelta64[m]')
    na = array_to_raw_qtemporal(na_dt, qtype=QMINUTE)
    assert na.dtype == numpy.int32
    for x in range(len(na)):
        assert na[x] == -1000000 + x * 12345

    na_dt = numpy.arange(-1000000, 1000000, 12345, dtype='timedelta64[ms]')
    na = array_to_raw_qtemporal(na_dt, qtype=QTIME)
    assert na.dtype == numpy.int32
    for x in range(len(na)):
        assert na[x] == -1000000 + x * 12345

    na_dt = numpy.arange(-1000000, 1000000, 12345, dtype='timedelta64[s]')
    na = array_to_raw_qtemporal(na_dt, qtype=QSECOND)
    assert na.dtype == numpy.int32
    for x in range(len(na)):
        assert na[x] == -1000000 + x * 12345

    na_dt = numpy.arange(-1000000, 1000000, 12345, dtype='timedelta64[ns]')
    na = array_to_raw_qtemporal(na_dt, qtype=QTIMESPAN)
    assert na.dtype == numpy.int64
    for x in range(len(na)):
        assert na[x] == -1000000 + x * 12345



def test_array_from_raw_qtemporal():
    raw = numpy.array([12, 121, qnull(QMONTH)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QMONTH)

    assert str(na_dt.dtype).startswith('datetime64[M]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.datetime64('NaT', 'M'):
            assert na_dt[x].astype(int) == raw[x] + 360
        else:
            assert raw[x] == qnull(QMONTH)

    raw = numpy.array([366, 121, qnull(QDATE)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QDATE)

    assert str(na_dt.dtype).startswith('datetime64[D]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.datetime64('NaT', 'D'):
            assert na_dt[x].astype(int) == raw[x] + 10957
        else:
            assert raw[x] == qnull(QDATE)

    raw = numpy.array([43500, -121, qnull(QMINUTE)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QMINUTE)

    assert str(na_dt.dtype).startswith('timedelta64[m]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.timedelta64('NaT', 'm'):
            assert na_dt[x].astype(int) == raw[x]
        else:
            assert raw[x] == qnull(QMINUTE)

    raw = numpy.array([43500, -121, qnull(QSECOND)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QSECOND)

    assert str(na_dt.dtype).startswith('timedelta64[s]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.timedelta64('NaT', 's'):
            assert na_dt[x].astype(int) == raw[x]
        else:
            assert raw[x] == qnull(QSECOND)

    raw = numpy.array([43500, -121, qnull(QTIME)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QTIME)

    assert str(na_dt.dtype).startswith('timedelta64[ms]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.timedelta64('NaT', 'ms'):
            assert na_dt[x].astype(int) == raw[x]
        else:
            assert raw[x] == qnull(QTIME)

    raw = numpy.array([20217600000000, -2021760000, qnull(QTIMESPAN)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QTIMESPAN)

    assert str(na_dt.dtype).startswith('timedelta64[ns]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.timedelta64('NaT', 'ns'):
            assert na_dt[x].astype(numpy.int64) == raw[x]
        else:
            assert raw[x] == qnull(QTIMESPAN)

    raw = numpy.array([279417600000000, -2021760000, qnull(QTIMESTAMP)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QTIMESTAMP)

    assert str(na_dt.dtype).startswith('datetime64[ns]')
    for x in range(len(na_dt)):
        if na_dt[x] != numpy.datetime64('NaT', 'ns'):
            assert na_dt[x].astype(numpy.int64) == raw[x] + numpy.datetime64('2000-01-01T00:00:00Z', 'ns').astype(numpy.int64)
        else:
            assert raw[x] == qnull(QTIMESTAMP)


    raw = numpy.array([3.234, qnull(QDATETIME)])
    na_dt = array_from_raw_qtemporal(raw, qtype=QDATETIME)
    ref = numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), numpy.datetime64('nat', 'ms')])

    assert str(na_dt.dtype).startswith('datetime64[ms]')
    for x in range(len(na_dt)):
        assert na_dt[x] == ref[x]


test_is_null()
test_qdict()
test_qtable()
test_qkeyedtable()
test_qtemporallist()
test_array_to_raw_qtemporal()
test_array_from_raw_qtemporal()
