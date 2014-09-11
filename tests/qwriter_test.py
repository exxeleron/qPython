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
import sys

from collections import OrderedDict
from qpython import qwriter
from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import qlist, QDictionary, qtable, QKeyedTable
from qpython.qtemporal import qtemporal, to_raw_qtemporal

BINARY = OrderedDict()

EXPRESSIONS = OrderedDict((
                   ('("G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"; 0Ng)',
                                                                     qlist(numpy.array([uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661'), qnull(QGUID)]), qtype=QGUID_LIST)),
                   ('"G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"',    uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661')),
                   ('"G"$"00000000-0000-0000-0000-000000000000"',    uuid.UUID('00000000-0000-0000-0000-000000000000')),
                   ('(2001.01m; 0Nm)',                               (qlist(numpy.array([to_raw_qtemporal(numpy.datetime64('2001-01', 'M'), QMONTH), qnull(QMONTH)]), qtype=QMONTH_LIST),
                                                                      qlist(numpy.array([12, qnull(QMONTH)]), qtype=QMONTH_LIST),
                                                                      qlist([12, qnull(QMONTH)], qtype=QMONTH_LIST))),
                   ('2001.01m',                                      qtemporal(numpy.datetime64('2001-01', 'M'), qtype=QMONTH)),
                   ('0Nm',                                           qtemporal(qnull(QMONTH), qtype=QMONTH)),
                   ('2001.01.01 2000.05.01 0Nd',                     (qlist(numpy.array([to_raw_qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE), to_raw_qtemporal(numpy.datetime64('2000-05-01', 'D'), qtype=QDATE), qnull(QDATE)]), qtype=QDATE_LIST),
                                                                      qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST),
                                                                      qlist([366, 121, qnull(QDATE)], qtype=QDATE_LIST))),
                   ('2001.01.01',                                    qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE)),
                   ('0Nd',                                           qtemporal(qnull(QDATE), qtype=QDATE)),
                   ('2000.01.04T05:36:57.600 0Nz',                   (qlist(numpy.array([3.234, qnull(QDATETIME)]), qtype=QDATETIME_LIST),
                                                                      qlist([3.234, qnull(QDATETIME)], qtype=QDATETIME_LIST))),
                   ('2000.01.04T05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600', 'ms'), qtype=QDATETIME)),
                   ('0Nz',                                           qtemporal(qnull(QDATETIME), qtype=QDATETIME)),
                   ('12:01 0Nu',                                     (qlist(numpy.array([721, qnull(QMINUTE)]), qtype=QMINUTE_LIST),
                                                                      qlist([721, qnull(QMINUTE)], qtype=QMINUTE_LIST))),
                   ('12:01',                                         qtemporal(numpy.timedelta64(721, 'm'), qtype=QMINUTE)),
                   ('0Nu',                                           qtemporal(qnull(QMINUTE), qtype=QMINUTE)),
                   ('12:05:00 0Nv',                                  (qlist(numpy.array([43500, qnull(QSECOND)]), qtype=QSECOND_LIST),
                                                                      qlist([43500, qnull(QSECOND)], qtype=QSECOND_LIST))),
                   ('12:05:00',                                      qtemporal(numpy.timedelta64(43500, 's'), qtype=QSECOND)),
                   ('0Nv',                                           qtemporal(qnull(QSECOND), qtype=QSECOND)),
                   ('12:04:59.123 0Nt',                              (qlist(numpy.array([43499123, qnull(QTIME)]), qtype=QTIME_LIST),
                                                                      qlist([43499123, qnull(QTIME)], qtype=QTIME_LIST))),
                   ('12:04:59.123',                                  qtemporal(numpy.timedelta64(43499123, 'ms'), qtype=QTIME)),
                   ('0Nt',                                           qtemporal(qnull(QTIME), qtype=QTIME)),
                   ('2000.01.04D05:36:57.600 0Np',                   (qlist(numpy.array([long(279417600000000), qnull(QTIMESTAMP)]), qtype=QTIMESTAMP_LIST),
                                                                      qlist([long(279417600000000), qnull(QTIMESTAMP)], qtype=QTIMESTAMP_LIST))),
                   ('2000.01.04D05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600', 'ns'), qtype=QTIMESTAMP)),
                   ('0Np',                                           qtemporal(qnull(QTIMESTAMP), qtype=QTIMESTAMP)),
                   ('0D05:36:57.600 0Nn',                            (qlist(numpy.array([long(20217600000000), qnull(QTIMESPAN)]), qtype=QTIMESPAN_LIST),
                                                                      qlist([long(20217600000000), qnull(QTIMESPAN)], qtype=QTIMESPAN_LIST))),
                   ('0D05:36:57.600',                                qtemporal(numpy.timedelta64(20217600000000, 'ns'), qtype=QTIMESPAN)),
                   ('0Nn',                                           qtemporal(qnull(QTIMESPAN), qtype=QTIMESPAN)),
                  
                   ('::',                                            None),
                   ('1+`',                                           QException('type')),
                   ('1',                                             numpy.int64(1)),
                   ('1i',                                            numpy.int32(1)),
                   ('-234h',                                         numpy.int16(-234)),
                   ('0b',                                            numpy.bool_(False)),
                   ('1b',                                            numpy.bool_(True)),
                   ('0x2a',                                          numpy.byte(0x2a)),
                   ('89421099511627575j',                            numpy.int64(89421099511627575L)),   
                   ('5.5e',                                          numpy.float32(5.5)),
                   ('3.234',                                         numpy.float64(3.234)),
                   ('"0"',                                           '0'),
                   ('"abc"',                                         ('abc',
                                                                      numpy.array(list('abc')))),
                   ('"quick brown fox jumps over a lazy dog"',       'quick brown fox jumps over a lazy dog'),
                   ('`abc',                                          numpy.string_('abc')),
                   ('`quickbrownfoxjumpsoveralazydog',               numpy.string_('quickbrownfoxjumpsoveralazydog')),
                   ('0Nh',                                           qnull(QSHORT)),
                   ('0N',                                            qnull(QLONG)),
                   ('0Ni',                                           qnull(QINT)),
                   ('0Nj',                                           qnull(QLONG)),
                   ('0Ne',                                           qnull(QFLOAT)),
                   ('0n',                                            qnull(QDOUBLE)),
                   ('" "',                                           qnull(QSTRING)),
                   ('`',                                             qnull(QSYMBOL)),
                   ('0Ng',                                           qnull(QGUID)),
                   ('()',                                            []),
                   ('(0b;1b;0b)',                                    (numpy.array([False, True, False], dtype=numpy.bool_), 
                                                                      qlist(numpy.array([False, True, False]), qtype = QBOOL_LIST),
                                                                      qlist([False, True, False], qtype = QBOOL_LIST))),
                   ('(0x01;0x02;0xff)',                              (numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte), 
                                                                      qlist(numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte), qtype = QBYTE_LIST),
                                                                      qlist(numpy.array([0x01, 0x02, 0xff]), qtype = QBYTE_LIST),
                                                                      qlist([0x01, 0x02, 0xff], qtype = QBYTE_LIST))),
                   ('(1h;2h;3h)',                                    (numpy.array([1, 2, 3], dtype=numpy.int16), 
                                                                      qlist(numpy.array([1, 2, 3], dtype=numpy.int16), qtype = QSHORT_LIST),
                                                                      qlist(numpy.array([1, 2, 3]), qtype = QSHORT_LIST),
                                                                      qlist([1, 2, 3], qtype = QSHORT_LIST))),
                   ('1 2 3',                                         (numpy.array([1, 2, 3], dtype=numpy.int64), 
                                                                      qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype = QLONG_LIST),
                                                                      qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                      qlist([1, 2, 3], qtype = QLONG_LIST))),
                   ('(1i;2i;3i)',                                    (numpy.array([1, 2, 3], dtype=numpy.int32), 
                                                                      qlist(numpy.array([1, 2, 3], dtype=numpy.int32), qtype = QINT_LIST),
                                                                      qlist(numpy.array([1, 2, 3]), qtype = QINT_LIST),
                                                                      qlist([1, 2, 3], qtype = QINT_LIST))),
                   ('(1j;2j;3j)',                                    (numpy.array([1, 2, 3], dtype=numpy.int64), 
                                                                      qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype = QLONG_LIST),
                                                                      qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                      qlist([1, 2, 3], qtype = QLONG_LIST))),
                   ('(5.5e; 8.5e)',                                  (numpy.array([5.5, 8.5], dtype=numpy.float32), 
                                                                      qlist(numpy.array([5.5, 8.5], dtype=numpy.float32), qtype = QFLOAT_LIST),
                                                                      qlist(numpy.array([5.5, 8.5]), qtype = QFLOAT_LIST),
                                                                      qlist([5.5, 8.5], qtype = QFLOAT_LIST))),
                   ('3.23 6.46',                                     (numpy.array([3.23, 6.46], dtype=numpy.float64), 
                                                                      qlist(numpy.array([3.23, 6.46], dtype=numpy.float64), qtype = QDOUBLE_LIST),
                                                                      qlist(numpy.array([3.23, 6.46]), qtype = QDOUBLE_LIST),
                                                                      qlist([3.23, 6.46], qtype = QDOUBLE_LIST))),
                   ('(1;`bcd;"0bc";5.5e)',                           [numpy.int64(1), numpy.string_('bcd'), '0bc', numpy.float32(5.5)]),
                   ('(42;::;`foo)',                                  [numpy.int64(42), None, numpy.string_('foo')]),
                   ('(1;2h;3.234;"4")',                              [numpy.int64(1), numpy.int16(2), numpy.float64(3.234), '4']),
                   ('(`one;2 3;"456";(7;8 9))',                      [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), '456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]]),
                   
                   ('`jumps`over`a`lazy`dog',                        (numpy.array(['jumps', 'over', 'a', 'lazy', 'dog'], dtype=numpy.string_), 
                                                                      qlist(numpy.array(['jumps', 'over', 'a', 'lazy', 'dog']), qtype = QSYMBOL_LIST),
                                                                      qlist(['jumps', 'over', 'a', 'lazy', 'dog'], qtype = QSYMBOL_LIST))),
                   ('`the`quick`brown`fox',                          numpy.array([numpy.string_('the'), numpy.string_('quick'), numpy.string_('brown'), numpy.string_('fox')], dtype=numpy.object)),
                   ('``quick``fox',                                  qlist(numpy.array([qnull(QSYMBOL), numpy.string_('quick'), qnull(QSYMBOL), numpy.string_('fox')], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                   ('``',                                            qlist(numpy.array([qnull(QSYMBOL), qnull(QSYMBOL)], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                   ('("quick"; "brown"; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                     (['quick', 'brown', 'fox', 'jumps', 'over', 'a lazy', 'dog'],
                                                                      qlist(numpy.array(['quick', 'brown', 'fox', 'jumps', 'over', 'a lazy', 'dog']), qtype = QSTRING_LIST),
                                                                      qlist(['quick', 'brown', 'fox', 'jumps', 'over', 'a lazy', 'dog'], qtype = QSTRING_LIST))),
                   ('{x+y}',                                         QLambda('{x+y}')),
                   ('{x+y}[3]',                                      QLambda('{x+y}', numpy.int64(3))),
                   
                   ('(enlist `a)!(enlist 1)',                        (QDictionary(qlist(numpy.array(['a']), qtype = QSYMBOL_LIST), 
                                                                                  qlist(numpy.array([1], dtype=numpy.int64), qtype=QLONG_LIST)),
                                                                      QDictionary(qlist(numpy.array(['a']), qtype = QSYMBOL_LIST), 
                                                                                  qlist(numpy.array([1]), qtype=QLONG_LIST)))),
                   ('1 2!`abc`cdefgh',                               QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
                                                                                 qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST))),
                   ('`abc`def`gh!([] one: 1 2 3; two: 4 5 6)',       QDictionary(qlist(numpy.array(['abc', 'def', 'gh']), qtype = QSYMBOL_LIST),
                                                                                 qtable(qlist(numpy.array(['one', 'two']), qtype = QSYMBOL_LIST), 
                                                                                        [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST), 
                                                                                         qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)]))),
                   ('(`x`y!(`a;2))',                                 QDictionary(qlist(numpy.array(['x', 'y']), qtype = QSYMBOL_LIST), 
                                                                                 [numpy.string_('a'), numpy.int64(2)])),
                   ('(0 1; 2 3)!`first`second',                      QDictionary([qlist(numpy.array([0, 1], dtype=numpy.int64), qtype=QLONG_LIST), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST)],
                                                                                  qlist(numpy.array(['first', 'second']), qtype = QSYMBOL_LIST))),
                   ('(1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))',     QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), '4'],
                                                                                 [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), '456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]])),
                   ('`A`B`C!((1;3.234;3);(`x`y!(`a;2));5.5e)',       QDictionary(qlist(numpy.array(['A', 'B', 'C']), qtype = QSYMBOL_LIST),
                                                                                 [[numpy.int64(1), numpy.float64(3.234), numpy.int64(3)], QDictionary(qlist(numpy.array(['x', 'y']), qtype = QSYMBOL_LIST), [numpy.string_('a'), numpy.int64(2)]), numpy.float32(5.5)])),
                   
                   ('flip `abc`def!(1 2 3; 4 5 6)',                  (qtable(qlist(numpy.array(['abc', 'def']), qtype = QSYMBOL_LIST), 
                                                                            [qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype=QLONG_LIST), 
                                                                             qlist(numpy.array([4, 5, 6], dtype=numpy.int64), qtype=QLONG_LIST)], 
                                                                            qtype=QTABLE),
                                                                      qtable(qlist(numpy.array(['abc', 'def']), qtype = QSYMBOL_LIST), 
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST), 
                                                                              qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)]),
                                                                      qtable(qlist(['abc', 'def'], qtype = QSYMBOL_LIST), 
                                                                             [qlist([1, 2, 3], qtype = QLONG_LIST), 
                                                                              qlist([4, 5, 6], qtype = QLONG_LIST)]),
                                                                      qtable(qlist(['abc', 'def'], qtype = QSYMBOL_LIST), 
                                                                             [qlist([1, 2, 3]), qlist([4, 5, 6])],
                                                                             **{'abc': QLONG_LIST, 'def': QLONG_LIST}),
                                                                      qtable(['abc', 'def'], 
                                                                             [[1, 2, 3], [4, 5, 6]],
                                                                             **{'abc': QLONG, 'def': QLONG}))),
                   ('flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)',
                                                                     (qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                             qlist(numpy.array([98, 42, 126], dtype=numpy.int64), qtype = QLONG_LIST)]),
                                                                      qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST)]),
                                                                      qtable(qlist(['name', 'iq'], qtype = QSYMBOL_LIST),
                                                                             [qlist(['Dent', 'Beeblebrox', 'Prefect'], qtype = QSYMBOL_LIST), 
                                                                              qlist([98, 42, 126], qtype = QLONG_LIST)]),
                                                                      qtable(qlist(['name', 'iq'], qtype = QSYMBOL_LIST),
                                                                             [qlist(['Dent', 'Beeblebrox', 'Prefect']), 
                                                                              qlist([98, 42, 126])],
                                                                             name = QSYMBOL, iq = QLONG),
                                                                      qtable(['name', 'iq'],
                                                                             [['Dent', 'Beeblebrox', 'Prefect'], 
                                                                              [98, 42, 126]],
                                                                             name = QSYMBOL, iq = QLONG),
                                                                      qtable(['name', 'iq'],
                                                                             [['Dent', 'Beeblebrox', 'Prefect'], 
                                                                              [98, 42, 126]],
                                                                             **{'name': QSYMBOL, 'iq': QLONG}))),
                   ('flip `name`iq`grade!(`Dent`Beeblebrox`Prefect;98 42 126;"a c")',
                                                                      qtable(qlist(numpy.array(['name', 'iq', 'grade']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                              "a c"])),
                   ('flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))',
                                                                       qtable(qlist(numpy.array(['name', 'iq', 'fullname']), qtype = QSYMBOL_LIST),
                                                                              [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                               qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array(["Arthur Dent", "Zaphod Beeblebrox", "Ford Prefect"]), qtype = QSTRING_LIST)])),
                   ('flip `name`iq`misc!(`Dent`Beeblebrox`Prefect;98 42 126;("The Hitch Hiker\'s Guide to the Galaxy"; 160; 1979.10.12))',
                                                                       qtable(qlist(numpy.array(['name', 'iq', 'misc']), qtype = QSYMBOL_LIST),
                                                                              [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                               qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array(["The Hitch Hiker\'s Guide to the Galaxy", 160L, qtemporal(numpy.datetime64('1979-10-12', 'D'), qtype=QDATE)]), qtype = QGENERAL_LIST)])),
                   ('([] sc:1 2 3; nsc:(1 2; 3 4; 5 6 7))',          (qtable(qlist(numpy.array(['sc', 'nsc']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype = QLONG_LIST),
                                                                             [qlist(numpy.array([1, 2], dtype=numpy.int64), qtype = QLONG_LIST),
                                                                              qlist(numpy.array([3, 4], dtype=numpy.int64), qtype = QLONG_LIST),
                                                                              qlist(numpy.array([5, 6, 7], dtype=numpy.int64), qtype = QLONG_LIST)]]),
                                                                      qtable(qlist(numpy.array(['sc', 'nsc']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                              [qlist(numpy.array([1, 2]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([3, 4]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([5, 6, 7]), qtype = QLONG_LIST)]]),
                                                                      qtable(qlist(['sc', 'nsc'], qtype = QSYMBOL_LIST),
                                                                             [qlist([1, 2, 3], qtype = QLONG_LIST),
                                                                              [qlist([1, 2], qtype = QLONG_LIST),
                                                                               qlist([3, 4], qtype = QLONG_LIST),
                                                                               qlist([5, 6, 7], qtype = QLONG_LIST)]]))),
                   ('([] name:`symbol$(); iq:`int$())',              (qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array([], dtype=numpy.string_), qtype = QSYMBOL_LIST), 
                                                                             qlist(numpy.array([], dtype=numpy.int32), qtype = QINT_LIST)]), 
                                                                      qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array([]), qtype = QSYMBOL_LIST), 
                                                                             qlist(numpy.array([]), qtype = QINT_LIST)]),
                                                                      qtable(qlist(['name', 'iq'], qtype = QSYMBOL_LIST),
                                                                            [qlist([], qtype = QSYMBOL_LIST), 
                                                                             qlist([], qtype = QINT_LIST)]))),
                   ('([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))', 
                                                                     qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
                                                                             qlist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)])),
                   ('([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                      QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array([1001, 1002, 1003]), qtype = QLONG_LIST)]),
                                                                                  qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
                                                                                          qlist(numpy.array([366, 121, qnull(QDATE)]), qtype = QDATE_LIST)]))
                                                                      ),
                ))



def init():
    with open('tests/QExpressions3.out', 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary



def test_writing():
    w = qwriter.QWriter(None, 3)
    
    for query, value in EXPRESSIONS.iteritems():
        sys.stdout.write( '%-75s' % query )
        if isinstance(value, tuple):
            for object in value:
                sys.stdout.write( '.' )
                serialized = binascii.hexlify(w.write(object, 1))[16:].lower()
                assert serialized == BINARY[query].lower(), 'serialization failed: %s, expected: %s actual: %s' % (object,  BINARY[query].lower(), serialized)
        else:
            sys.stdout.write( '.' )
            serialized = binascii.hexlify(w.write(value, 1))[16:].lower()
            assert serialized == BINARY[query].lower(), 'serialization failed: %s, expected: %s actual: %s' % (value,  BINARY[query].lower(), serialized)
        
        print ''        
        


init()
test_writing()