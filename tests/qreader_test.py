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

import binascii
import os
import struct
import sys
try:
    from cStringIO import BytesIO
except ImportError:
    from io import BytesIO

if sys.version > '3':
    long = int

from collections import OrderedDict
from qpython import qreader
from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import qlist, QList, QTemporalList, QDictionary, qtable, QKeyedTable
from qpython.qtemporal import qtemporal, QTemporal

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')


EXPRESSIONS = OrderedDict((
                    (b'("G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"; 0Ng)',
                                                                      qlist(numpy.array([uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661'), qnull(QGUID)]), qtype=QGUID_LIST)),
                    (b'"G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"',    uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661')),
                    (b'"G"$"00000000-0000-0000-0000-000000000000"',    uuid.UUID('00000000-0000-0000-0000-000000000000')),
                    (b'(2001.01m; 0Nm)',                               qlist(numpy.array([12, qnull(QMONTH)]), qtype=QMONTH_LIST)),
                    (b'2001.01m',                                      qtemporal(numpy.datetime64('2001-01', 'M'), qtype=QMONTH)),
                    (b'0Nm',                                           qtemporal(numpy.datetime64('NaT', 'M'), qtype=QMONTH)),
                    (b'2001.01.01 2000.05.01 0Nd',                     qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)),
                    (b'2001.01.01',                                    qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE)),
                    (b'0Nd',                                           qtemporal(numpy.datetime64('NaT', 'D'), qtype=QDATE)),
                    (b'2000.01.04T05:36:57.600 0Nz',                   qlist(numpy.array([3.234, qnull(QDATETIME)]), qtype=QDATETIME_LIST)),
                    (b'2000.01.04T05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), qtype=QDATETIME)),
                    (b'0Nz',                                           qtemporal(numpy.datetime64('NaT', 'ms'), qtype=QDATETIME)),
                    (b'12:01 0Nu',                                     qlist(numpy.array([721, qnull(QMINUTE)]), qtype=QMINUTE_LIST)),
                    (b'12:01',                                         qtemporal(numpy.timedelta64(721, 'm'), qtype=QMINUTE)),
                    (b'0Nu',                                           qtemporal(numpy.timedelta64('NaT', 'm'), qtype=QMINUTE)),
                    (b'12:05:00 0Nv',                                  qlist(numpy.array([43500, qnull(QSECOND)]), qtype=QSECOND_LIST)),
                    (b'12:05:00',                                      qtemporal(numpy.timedelta64(43500, 's'), qtype=QSECOND)),
                    (b'0Nv',                                           qtemporal(numpy.timedelta64('NaT', 's'), qtype=QSECOND)),
                    (b'12:04:59.123 0Nt',                              qlist(numpy.array([43499123, qnull(QTIME)]), qtype=QTIME_LIST)),
                    (b'12:04:59.123',                                  qtemporal(numpy.timedelta64(43499123, 'ms'), qtype=QTIME)),
                    (b'0Nt',                                           qtemporal(numpy.timedelta64('NaT', 'ms'), qtype=QTIME)),
                    (b'2000.01.04D05:36:57.600 0Np',                   qlist(numpy.array([long(279417600000000), qnull(QTIMESTAMP)]), qtype=QTIMESTAMP_LIST)),
                    (b'2000.01.04D05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600Z', 'ns'), qtype=QTIMESTAMP)),
                    (b'0Np',                                           qtemporal(numpy.datetime64('NaT', 'ns'), qtype=QTIMESTAMP)),
                    (b'0D05:36:57.600 0Nn',                            qlist(numpy.array([long(20217600000000), qnull(QTIMESPAN)]), qtype=QTIMESPAN_LIST)),
                    (b'0D05:36:57.600',                                qtemporal(numpy.timedelta64(20217600000000, 'ns'), qtype=QTIMESPAN)),
                    (b'0Nn',                                           qtemporal(numpy.timedelta64('NaT', 'ns'), qtype=QTIMESPAN)),

                    (b'::',                                            None),
                    (b'1+`',                                           QException(b'type')),
                    (b'1',                                             numpy.int64(1)),
                    (b'1i',                                            numpy.int32(1)),
                    (b'-234h',                                         numpy.int16(-234)),
                    (b'0b',                                            numpy.bool_(False)),
                    (b'1b',                                            numpy.bool_(True)),
                    (b'0x2a',                                          numpy.byte(0x2a)),
                    (b'89421099511627575j',                            numpy.int64(long(89421099511627575))),
                    (b'5.5e',                                          numpy.float32(5.5)),
                    (b'3.234',                                         numpy.float64(3.234)),
                    (b'"0"',                                           b'0'),
                    (b'"abc"',                                         b'abc'),
                    (b'"quick brown fox jumps over a lazy dog"',       b'quick brown fox jumps over a lazy dog'),
                    (b'`abc',                                          numpy.string_('abc')),
                    (b'`quickbrownfoxjumpsoveralazydog',               numpy.string_('quickbrownfoxjumpsoveralazydog')),
                    (b'0Nh',                                           qnull(QSHORT)),
                    (b'0N',                                            qnull(QLONG)),
                    (b'0Ni',                                           qnull(QINT)),
                    (b'0Nj',                                           qnull(QLONG)),
                    (b'0Ne',                                           qnull(QFLOAT)),
                    (b'0n',                                            qnull(QDOUBLE)),
                    (b'" "',                                           qnull(QSTRING)),
                    (b'`',                                             qnull(QSYMBOL)),
                    (b'0Ng',                                           qnull(QGUID)),
                    (b'()',                                            []),
                    (b'(0b;1b;0b)',                                    qlist(numpy.array([False, True, False], dtype=numpy.bool_), qtype=QBOOL_LIST)),
                    (b'(0x01;0x02;0xff)',                              qlist(numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte), qtype=QBYTE_LIST)),
                    (b'(1h;2h;3h)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int16), qtype=QSHORT_LIST)),
                    (b'(1h;0Nh;3h)',                                   qlist(numpy.array([1, qnull(QSHORT), 3], dtype=numpy.int16), qtype=QSHORT_LIST)),
                    (b'1 2 3',                                         qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    (b'1 0N 3',                                        qlist(numpy.array([1, qnull(QLONG), 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    (b'(1i;2i;3i)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int32), qtype=QINT_LIST)),
                    (b'(1i;0Ni;3i)',                                   qlist(numpy.array([1, qnull(QINT), 3], dtype=numpy.int32), qtype=QINT_LIST)),
                    (b'(1j;2j;3j)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    (b'(1j;0Nj;3j)',                                   qlist(numpy.array([1, qnull(QLONG), 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    (b'(5.5e; 8.5e)',                                  qlist(numpy.array([5.5, 8.5], dtype=numpy.float32), qtype=QFLOAT_LIST)),
                    (b'(5.5e; 0Ne)',                                   qlist(numpy.array([5.5, qnull(QFLOAT)], dtype=numpy.float32), qtype=QFLOAT_LIST)),
                    (b'3.23 6.46',                                     qlist(numpy.array([3.23, 6.46], dtype=numpy.float64), qtype=QDOUBLE_LIST)),
                    (b'3.23 0n',                                       qlist(numpy.array([3.23, qnull(QDOUBLE)], dtype=numpy.float64), qtype=QDOUBLE_LIST)),
                    (b'(1;`bcd;"0bc";5.5e)',                           [numpy.int64(1), numpy.string_('bcd'), b'0bc', numpy.float32(5.5)]),
                    (b'(42;::;`foo)',                                  [numpy.int64(42), None, numpy.string_('foo')]),
                    (b'`the`quick`brown`fox',                          qlist(numpy.array([numpy.string_('the'), numpy.string_('quick'), numpy.string_('brown'), numpy.string_('fox')], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                    (b'``quick``fox',                                  qlist(numpy.array([qnull(QSYMBOL), numpy.string_('quick'), qnull(QSYMBOL), numpy.string_('fox')], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                    (b'``',                                            qlist(numpy.array([qnull(QSYMBOL), qnull(QSYMBOL)], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                    (b'("quick"; "brown"; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                      [b'quick', b'brown', b'fox', b'jumps', b'over', b'a lazy', b'dog']),
                    (b'("quick"; " "; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                      [b'quick', b' ', b'fox', b'jumps', b'over', b'a lazy', b'dog']),
                    (b'{x+y}',                                         QLambda('{x+y}')),
                    (b'{x+y}[3]',                                      QProjection([QLambda('{x+y}'), numpy.int64(3)])),
                    (b'insert [1]',                                    QProjection([QFunction(0), numpy.int64(1)])),
                    (b'xbar',                                          QLambda('k){x*y div x:$[16h=abs[@x];"j"$x;x]}')),
                    (b'not',                                           QFunction(0)),
                    (b'and',                                           QFunction(0)),
                    (b'md5',                                           QProjection([QFunction(0), numpy.int64(-15)])),
                    (b'any',                                           QFunction(0)),
                    (b'save',                                          QFunction(0)),
                    (b'raze',                                          QFunction(0)),
                    (b'sums',                                          QFunction(0)),
                    (b'prev',                                          QFunction(0)),

                    (b'(enlist `a)!(enlist 1)',                        QDictionary(qlist(numpy.array(['a']), qtype = QSYMBOL_LIST),
                                                                                  qlist(numpy.array([1], dtype=numpy.int64), qtype=QLONG_LIST))),
                    (b'1 2!`abc`cdefgh',                               QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
                                                                                  qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST))),
                    (b'`abc`def`gh!([] one: 1 2 3; two: 4 5 6)',       QDictionary(qlist(numpy.array(['abc', 'def', 'gh']), qtype = QSYMBOL_LIST),
                                                                                  qtable(qlist(numpy.array(['one', 'two']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                                          qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)]))),
                    (b'(0 1; 2 3)!`first`second',                      QDictionary([qlist(numpy.array([0, 1], dtype=numpy.int64), qtype=QLONG_LIST), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST)],
                                                                                   qlist(numpy.array(['first', 'second']), qtype = QSYMBOL_LIST))),
                    (b'(1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))',     QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), b'4'],
                                                                                  [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), b'456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]])),
                    (b'`A`B`C!((1;3.234;3);(`x`y!(`a;2));5.5e)',       QDictionary(qlist(numpy.array(['A', 'B', 'C']), qtype = QSYMBOL_LIST),
                                                                                  [[numpy.int64(1), numpy.float64(3.234), numpy.int64(3)], QDictionary(qlist(numpy.array(['x', 'y']), qtype = QSYMBOL_LIST), [b'a', numpy.int64(2)]), numpy.float32(5.5)])),

                    (b'flip `abc`def!(1 2 3; 4 5 6)',                  qtable(qlist(numpy.array(['abc', 'def']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                              qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)])),
                    (b'flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)',
                                                                      qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST),
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST)])),
                    (b'flip `name`iq`grade!(`Dent`Beeblebrox`Prefect;98 42 126;"a c")',
                                                                      qtable(qlist(numpy.array(['name', 'iq', 'grade']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST),
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                              b"a c"])),
                    (b'flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))',
                                                                      qtable(qlist(numpy.array(['name', 'iq', 'fullname']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST),
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                              [b"Arthur Dent", b"Zaphod Beeblebrox", b"Ford Prefect"]])),
                    (b'flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; " "; "Ford Prefect"))',
                                                                      qtable(qlist(numpy.array(['name', 'iq', 'fullname']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST),
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                              [b"Arthur Dent", b" ", b"Ford Prefect"]])),
                    (b'([] sc:1 2 3; nsc:(1 2; 3 4; 5 6 7))',         qtable(qlist(numpy.array(['sc', 'nsc']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                              [qlist(numpy.array([1, 2]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([3, 4]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([5, 6, 7]), qtype = QLONG_LIST)]])),
                    (b'([] sc:1 2 3; nsc:(1 2; 3 4; 5 6))',           qtable(qlist(numpy.array(['sc', 'nsc']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                              [qlist(numpy.array([1, 2]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([3, 4]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([5, 6]), qtype = QLONG_LIST)]])),
                    (b'1#([] sym:`x`x`x;str:"  a")',                  qtable(qlist(numpy.array(['sym', 'str']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['x'], dtype=numpy.string_), qtype = QSYMBOL_LIST),
                                                                             b" "])),
                    (b'-1#([] sym:`x`x`x;str:"  a")',                 qtable(qlist(numpy.array(['sym', 'str']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['x'], dtype=numpy.string_), qtype = QSYMBOL_LIST),
                                                                             b"a"])),
                    (b'2#([] sym:`x`x`x`x;str:"  aa")',               qtable(qlist(numpy.array(['sym', 'str']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['x', 'x'], dtype=numpy.string_), qtype = QSYMBOL_LIST),
                                                                             b"  "])),
                    (b'-2#([] sym:`x`x`x`x;str:"  aa")',              qtable(qlist(numpy.array(['sym', 'str']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['x', 'x'], dtype=numpy.string_), qtype = QSYMBOL_LIST),
                                                                             b"aa"])),
                    (b'([] name:`symbol$(); iq:`int$())',             qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array([], dtype=numpy.string_), qtype = QSYMBOL_LIST),
                                                                             qlist(numpy.array([]), qtype = QINT_LIST)])),
                    (b'([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                      qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST),
                                                                              qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)])),
                    (b'([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                      QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array([1001, 1002, 1003]), qtype = QLONG_LIST)]),
                                                                                  qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST),
                                                                                          qlist(numpy.array([366, 121, qnull(QDATE)]), qtype = QDATE_LIST)]))
                                                                      ),

                  ))


NUMPY_TEMPORAL_EXPRESSIONS = OrderedDict((
                    (b'(2001.01m; 0Nm)',                               qlist(numpy.array([numpy.datetime64('2001-01'), numpy.datetime64('NaT')], dtype='datetime64[M]'), qtype=QMONTH_LIST)),
                    (b'2001.01m',                                      numpy.datetime64('2001-01', 'M')),
                    (b'0Nm',                                           numpy.datetime64('NaT', 'M')),
                    (b'2001.01.01 2000.05.01 0Nd',                     qlist(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]'), qtype=QDATE_LIST)),
                    (b'2001.01.01',                                    numpy.datetime64('2001-01-01', 'D')),
                    (b'0Nd',                                           numpy.datetime64('NaT', 'D')),
                    (b'2000.01.04T05:36:57.600 0Nz',                   qlist(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), numpy.datetime64('nat', 'ms')]), qtype = QDATETIME_LIST)),
                    (b'2000.01.04T05:36:57.600',                       numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms')),
                    (b'0Nz',                                           numpy.datetime64('NaT', 'ms')),
                    (b'12:01 0Nu',                                     qlist(numpy.array([numpy.timedelta64(721, 'm'), numpy.timedelta64('nat', 'm')]), qtype = QMINUTE)),
                    (b'12:01',                                         numpy.timedelta64(721, 'm')),
                    (b'0Nu',                                           numpy.timedelta64('NaT', 'm')),
                    (b'12:05:00 0Nv',                                  qlist(numpy.array([numpy.timedelta64(43500, 's'), numpy.timedelta64('nat', 's')]), qtype = QSECOND)),
                    (b'12:05:00',                                      numpy.timedelta64(43500, 's')),
                    (b'0Nv',                                           numpy.timedelta64('nat', 's')),
                    (b'12:04:59.123 0Nt',                              qlist(numpy.array([numpy.timedelta64(43499123, 'ms'), numpy.timedelta64('nat', 'ms')]), qtype = QTIME_LIST)),
                    (b'12:04:59.123',                                  numpy.timedelta64(43499123, 'ms')),
                    (b'0Nt',                                           numpy.timedelta64('NaT', 'ms')),
                    (b'2000.01.04D05:36:57.600 0Np',                   qlist(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ns'), numpy.datetime64('nat', 'ns')]), qtype = QTIMESTAMP_LIST)),
                    (b'2000.01.04D05:36:57.600',                       numpy.datetime64('2000-01-04T05:36:57.600Z', 'ns')),
                    (b'0Np',                                           numpy.datetime64('NaT', 'ns')),
                    (b'0D05:36:57.600 0Nn',                            qlist(numpy.array([numpy.timedelta64(20217600000000, 'ns'), numpy.timedelta64('nat', 'ns')]), qtype = QTIMESPAN_LIST)),
                    (b'0D05:36:57.600',                                numpy.timedelta64(20217600000000, 'ns')),
                    (b'0Nn',                                           numpy.timedelta64('NaT', 'ns')),
                    (b'([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                      qtable(['pos', 'dates'],
                                                                            [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST),
                                                                             numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]')])),
                    ))



COMPRESSED_EXPRESSIONS = OrderedDict((
                    (b'1000#`q',                                        qlist(numpy.array(['q'] * 1000), qtype=QSYMBOL_LIST)),
                    (b'([] q:1000#`q)',                                 qtable(qlist(numpy.array(['q']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['q'] * 1000), qtype=QSYMBOL_LIST)])),
                    (b'([] a:til 200;b:25+til 200;c:200#`a)',           qtable(qlist(numpy.array(['a', 'b', 'c']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.arange(200), qtype=QLONG_LIST),
                                                                              qlist(numpy.arange(200) + 25, qtype=QLONG_LIST),
                                                                              qlist(numpy.array(['a'] * 200), qtype=QSYMBOL_LIST)])),
                   ))




def arrays_equal(left, right):
    if type(left) != type(right):
        return False

    if type(left) == numpy.ndarray and left.dtype != right.dtype:
        print('Type comparison failed: %s != %s' % (left.dtype, right.dtype))
        return False

    if type(left) == QList and left.meta.qtype != right.meta.qtype:
        print('QType comparison failed: %s != %s' % (left.meta.qtype, right.meta.qtype))
        return False

    if len(left) != len(right):
        return False

    for i in range(len(left)):
        if type(left[i]) != type(right[i]):
            print('Type comparison failed: %s != %s' % (type(left[i]), type(right[i])))
            return False

        if not compare(left[i], right[i]):
            print('Value comparison failed: %s != %s' % ( left[i], right[i]))
            return False

    return True


def compare(left, right):
    if type(left) in [float, numpy.float32, numpy.float64] and numpy.isnan(left):
        return numpy.isnan(right)
    if type(left) == QTemporal and isinstance(left.raw, float) and numpy.isnan(left.raw):
        return numpy.isnan(right.raw)
    elif type(left) in [list, tuple, numpy.ndarray, QList, QTemporalList]:
        return arrays_equal(left, right)
    elif type(left) == QFunction:
        return type(right) == QFunction
    else:
        return left == right


def test_reading():
    BINARY = OrderedDict()

    with open(os.path.join(TEST_DATA_DIR, 'QExpressions3.out'), 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary

    buffer_reader = qreader.QReader(None)
    print('Deserialization')
    for query, value in iter(EXPRESSIONS.items()):
        buffer_ = BytesIO()
        binary = binascii.unhexlify(BINARY[query])

        buffer_.write(b'\1\0\0\0')
        buffer_.write(struct.pack('i', len(binary) + 8))
        buffer_.write(binary)
        buffer_.seek(0)

        sys.stdout.write( '  %-75s' % query )
        try:
            header = buffer_reader.read_header(source = buffer_.getvalue())
            result = buffer_reader.read_data(message_size = header.size, is_compressed = header.is_compressed, raw = True)
            assert compare(buffer_.getvalue()[8:], result), 'raw reading failed: %s' % (query)

            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read(raw = True).data
            assert compare(buffer_.getvalue()[8:], result), 'raw reading failed: %s' % (query)

            result = buffer_reader.read(source = buffer_.getvalue()).data
            assert compare(value, result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value, result)

            header = buffer_reader.read_header(source = buffer_.getvalue())
            result = buffer_reader.read_data(message_size = header.size, is_compressed = header.is_compressed)
            assert compare(value, result), 'deserialization failed: %s' % (query)

            buffer_.seek(0)
            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read().data
            assert compare(value, result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value, result)
            print('.')
        except QException as e:
            assert isinstance(value, QException)
            assert e.args == value.args
            print('.')



def test_reading_numpy_temporals():
    BINARY = OrderedDict()

    with open('tests/QExpressions3.out', 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary

    print('Deserialization (numpy temporals)')
    for query, value in iter(NUMPY_TEMPORAL_EXPRESSIONS.items()):
        buffer_ = BytesIO()
        binary = binascii.unhexlify(BINARY[query])

        buffer_.write(b'\1\0\0\0')
        buffer_.write(struct.pack('i', len(binary) + 8))
        buffer_.write(binary)
        buffer_.seek(0)

        sys.stdout.write( '  %-75s' % query )
        try:
            buffer_.seek(0)
            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read(numpy_temporals = True).data
            assert compare(value, result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value, result)
            print('.')
        except QException as e:
            assert isinstance(value, QException)
            assert e.args == value.args
            print('.')



def test_reading_compressed():
    BINARY = OrderedDict()

    with open('tests/QCompressedExpressions3.out', 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary

    print('Compressed deserialization')
    buffer_reader = qreader.QReader(None)
    for query, value in iter(COMPRESSED_EXPRESSIONS.items()):
        buffer_ = BytesIO()
        binary = binascii.unhexlify(BINARY[query])

        buffer_.write(b'\1\0\1\0')
        buffer_.write(struct.pack('i', len(binary) + 8))
        buffer_.write(binary)
        buffer_.seek(0)

        sys.stdout.write( '  %-75s' % query )
        try:
            result = buffer_reader.read(source = buffer_.getvalue()).data
            assert compare(value, result), 'deserialization failed: %s' % (query)

            header = buffer_reader.read_header(source = buffer_.getvalue())
            result = buffer_reader.read_data(message_size = header.size, is_compressed = header.is_compressed)
            assert compare(value, result), 'deserialization failed: %s' % (query)

            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read().data
            assert compare(value, result), 'deserialization failed: %s' % (query)
            print('.')
        except QException as e:
            assert isinstance(value, QException)
            assert e.args == value.args
            print('.')



test_reading()
test_reading_numpy_temporals()
test_reading_compressed()
