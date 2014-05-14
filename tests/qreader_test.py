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
import cStringIO
import struct
import sys

from collections import OrderedDict
from qpython import qreader
from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import qlist, QList, QDictionary, qtable, QKeyedTable
from qpython.qtemporal import qtemporal, QTemporal, qtemporallist, QTemporalList



EXPRESSIONS = OrderedDict((
                    ('("G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"; 0Ng)',
                                                                      qlist(numpy.array([uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661'), qnull(QGUID)]), qtype=QGUID_LIST)),
                    ('"G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"',    uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661')),
                    ('"G"$"00000000-0000-0000-0000-000000000000"',    uuid.UUID('00000000-0000-0000-0000-000000000000')),
                    ('(2001.01m; 0Nm)',                               qtemporallist(numpy.array([12, qnull(QMONTH)]), qtype=QMONTH_LIST)),
                    ('2001.01m',                                      qtemporal(numpy.datetime64('2001-01', 'M'), qtype=QMONTH)),
                    ('0Nm',                                           qtemporal(qnull(QMONTH), qtype=QMONTH)),
                    ('2001.01.01 2000.05.01 0Nd',                     qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)),
                    ('2001.01.01',                                    qtemporal(numpy.datetime64('2001-01-01', 'D'), qtype=QDATE)),
                    ('0Nd',                                           qtemporal(qnull(QDATE), qtype=QDATE)),
                    ('2000.01.04T05:36:57.600 0Nz',                   qtemporallist(numpy.array([3.234, qnull(QDATETIME)]), qtype=QDATETIME_LIST)),
                    ('2000.01.04T05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600', 'ms'), qtype=QDATETIME)),
                    ('0Nz',                                           qtemporal(qnull(QDATETIME), qtype=QDATETIME)),
                    ('12:01 0Nu',                                     qtemporallist(numpy.array([721, qnull(QMINUTE)]), qtype=QMINUTE_LIST)),
                    ('12:01',                                         qtemporal(numpy.timedelta64(721, 'm'), qtype=QMINUTE)),
                    ('0Nu',                                           qtemporal(qnull(QMINUTE), qtype=QMINUTE)),
                    ('12:05:00 0Nv',                                  qtemporallist(numpy.array([43500, qnull(QSECOND)]), qtype=QSECOND_LIST)),
                    ('12:05:00',                                      qtemporal(numpy.timedelta64(43500, 's'), qtype=QSECOND)),
                    ('0Nv',                                           qtemporal(qnull(QSECOND), qtype=QSECOND)),
                    ('12:04:59.123 0Nt',                              qtemporallist(numpy.array([43499123, qnull(QTIME)]), qtype=QTIME_LIST)),
                    ('12:04:59.123',                                  qtemporal(numpy.timedelta64(43499123, 'ms'), qtype=QTIME)),
                    ('0Nt',                                           qtemporal(qnull(QTIME), qtype=QTIME)),
                    ('2000.01.04D05:36:57.600 0Np',                   qtemporallist(numpy.array([long(279417600000000), qnull(QTIMESTAMP)]), qtype=QTIMESTAMP_LIST)),
                    ('2000.01.04D05:36:57.600',                       qtemporal(numpy.datetime64('2000-01-04T05:36:57.600', 'ns'), qtype=QTIMESTAMP)),
                    ('0Np',                                           qtemporal(qnull(QTIMESTAMP), qtype=QTIMESTAMP)),
                    ('0D05:36:57.600 0Nn',                            qtemporallist(numpy.array([long(20217600000000), qnull(QTIMESPAN)]), qtype=QTIMESPAN_LIST)),
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
                    ('"abc"',                                         'abc'),
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
                    ('()',                                            []),
                    ('(0b;1b;0b)',                                    qlist(numpy.array([False, True, False], dtype=numpy.bool_), qtype=QBOOL_LIST)),
                    ('(0x01;0x02;0xff)',                              qlist(numpy.array([0x01, 0x02, 0xff], dtype=numpy.byte), qtype=QBYTE_LIST)),
                    ('(1h;2h;3h)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int16), qtype=QSHORT_LIST)),
                    ('1 2 3',                                         qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    ('(1i;2i;3i)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int32), qtype=QINT_LIST)),
                    ('(1j;2j;3j)',                                    qlist(numpy.array([1, 2, 3], dtype=numpy.int64), qtype=QLONG_LIST)),
                    ('(5.5e; 8.5e)',                                  qlist(numpy.array([5.5, 8.5], dtype=numpy.float32), qtype=QFLOAT_LIST)),
                    ('3.23 6.46',                                     qlist(numpy.array([3.23, 6.46], dtype=numpy.float64), qtype=QDOUBLE_LIST)),
                    ('(1;`bcd;"0bc";5.5e)',                           [numpy.int64(1), numpy.string_('bcd'), '0bc', numpy.float32(5.5)]),
                    ('`the`quick`brown`fox',                          qlist(numpy.array([numpy.string_('the'), numpy.string_('quick'), numpy.string_('brown'), numpy.string_('fox')], dtype=numpy.object), qtype=QSYMBOL_LIST)),
                    ('{x+y}',                                         QLambda('{x+y}')),
                    ('{x+y}[3]',                                      QLambda('{x+y}', numpy.int64(3))),
                     
                    ('(enlist `a)!(enlist 1)',                        QDictionary(qlist(numpy.array(['a']), qtype = QSYMBOL_LIST), 
                                                                                  qlist(numpy.array([1], dtype=numpy.int64), qtype=QLONG_LIST))),
                    ('1 2!`abc`cdefgh',                               QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
                                                                                  qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST))),
                    ('(0 1; 2 3)!`first`second',                      QDictionary([qlist(numpy.array([0, 1], dtype=numpy.int64), qtype=QLONG_LIST), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST)],
                                                                                   qlist(numpy.array(['first', 'second']), qtype = QSYMBOL_LIST))),
                    ('(1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))',     QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), '4'],
                                                                                  [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), '456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]])),
                    ('`A`B`C!((1;3.234;3);(`x`y!(`a;2));5.5e)',       QDictionary(qlist(numpy.array(['A', 'B', 'C']), qtype = QSYMBOL_LIST),
                                                                                  [[numpy.int64(1), numpy.float64(3.234), numpy.int64(3)], QDictionary(qlist(numpy.array(['x', 'y']), qtype = QSYMBOL_LIST), ['a', numpy.int64(2)]), numpy.float32(5.5)])),
                     
                    ('flip `abc`def!(1 2 3; 4 5 6)',                  qtable(qlist(numpy.array(['abc', 'def']), qtype = QSYMBOL_LIST), 
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST), 
                                                                              qlist(numpy.array([4, 5, 6]), qtype = QLONG_LIST)])),
                    ('flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)',
                                                                      qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST)])),
                    ('flip `name`iq`grade!(`Dent`Beeblebrox`Prefect;98 42 126;"a c")',
                                                                      qtable(qlist(numpy.array(['name', 'iq', 'grade']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['Dent', 'Beeblebrox', 'Prefect']), qtype = QSYMBOL_LIST), 
                                                                              qlist(numpy.array([98, 42, 126]), qtype = QLONG_LIST),
                                                                              "a c"])),
                    ('([] sc:1 2 3; nsc:(1 2; 3 4; 5 6 7))',          qtable(qlist(numpy.array(['sc', 'nsc']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array([1, 2, 3]), qtype = QLONG_LIST),
                                                                              [qlist(numpy.array([1, 2]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([3, 4]), qtype = QLONG_LIST),
                                                                               qlist(numpy.array([5, 6, 7]), qtype = QLONG_LIST)]])),
                    ('([] name:`symbol$(); iq:`int$())',              qtable(qlist(numpy.array(['name', 'iq']), qtype = QSYMBOL_LIST),
                                                                            [qlist(numpy.array([], dtype=numpy.string_), qtype = QSYMBOL_LIST), 
                                                                             qlist(numpy.array([]), qtype = QINT_LIST)])),
                    ('([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))', 
                                                                      qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
                                                                              qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype=QDATE_LIST)])),
                    ('([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                      QKeyedTable(qtable(qlist(numpy.array(['eid']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array([1001, 1002, 1003]), qtype = QLONG_LIST)]),
                                                                                  qtable(qlist(numpy.array(['pos', 'dates']), qtype = QSYMBOL_LIST),
                                                                                         [qlist(numpy.array(['d1', 'd2', 'd3']), qtype = QSYMBOL_LIST), 
                                                                                          qtemporallist(numpy.array([366, 121, qnull(QDATE)]), qtype = QDATE_LIST)]))
                                                                      ),
                                                                                 
                  ))


COMPRESSED_EXPRESSIONS = OrderedDict((
                    ('1000#`q',                                        qlist(numpy.array(['q'] * 1000), qtype=QSYMBOL_LIST)),
                    ('([] q:1000#`q)',                                 qtable(qlist(numpy.array(['q']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.array(['q'] * 1000), qtype=QSYMBOL_LIST)])),
                    ('([] a:til 200;b:25+til 200;c:200#`a)',           qtable(qlist(numpy.array(['a', 'b', 'c']), qtype = QSYMBOL_LIST),
                                                                             [qlist(numpy.arange(200), qtype=QLONG_LIST),
                                                                              qlist(numpy.arange(200) + 25, qtype=QLONG_LIST),
                                                                              qlist(numpy.array(['a'] * 200), qtype=QSYMBOL_LIST)])),
                   ))




def arrays_equal(left, right):
    if type(left) != type(right):
        return False
    
    if type(left) == numpy.ndarray and left.dtype != right.dtype:
        print 'Type comparison failed: %s != %s' % (left.dtype, right.dtype)
        return False
    
    if type(left) == QList and left.meta.qtype != right.meta.qtype:
        print 'QType comparison failed: %s != %s' % (left.meta.qtype, right.meta.qtype)
        return False
    
    if len(left) != len(right):
        return False
    
    for i in xrange(len(left)):
        if type(left[i]) != type(right[i]):
            print 'Type comparison failed: %s != %s' % (type(left[i]), type(right[i]))
            return False
    
        if not compare(left[i], right[i]):
            print 'Value comparison failed: %s != %s' % ( left[i], right[i])
            return False

    return True


def compare(left, right):
    if type(left) in [float, numpy.float32, numpy.float64] and numpy.isnan(left):
        return numpy.isnan(right)
    if type(left) == QTemporal and isinstance(left.raw, float) and numpy.isnan(left.raw):
        return numpy.isnan(right.raw)
    elif type(left) in [list, tuple, numpy.ndarray, QList, QTemporalList]:
        return arrays_equal(left, right)
    else:
        return left == right


def test_reading():
    BINARY = OrderedDict()
    
    with open('tests/QExpressions3.out', 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary

    buffer_reader = qreader.QReader(None)
    print 'Deserialization'
    for query, value in EXPRESSIONS.iteritems():
        buffer_ = cStringIO.StringIO()
        binary = binascii.unhexlify(BINARY[query])
        
        buffer_.write('\1\0\0\0')
        buffer_.write(struct.pack('i', len(binary) + 8))
        buffer_.write(binary)
        buffer_.seek(0)
        
        sys.stdout.write( '  %-75s' % query )
        try:
            result = buffer_reader.read(source = buffer_.getvalue()).data
            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read().data
            assert compare(value, result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value, result)
            print '.'
        except QException, e:
            assert isinstance(value, QException)
            assert e.message == value.message
            print '.'


def test_reading_compressed():
    BINARY = OrderedDict()
    
    with open('tests/QCompressedExpressions3.out', 'rb') as f:
        while True:
            query = f.readline().strip()
            binary = f.readline().strip()

            if not binary:
                break

            BINARY[query] = binary
          
    print 'Compressed deserialization'  
    buffer_reader = qreader.QReader(None)
    for query, value in COMPRESSED_EXPRESSIONS.iteritems():
        buffer_ = cStringIO.StringIO()
        binary = binascii.unhexlify(BINARY[query])
        
        buffer_.write('\1\0\1\0')
        buffer_.write(struct.pack('i', len(binary) + 8))
        buffer_.write(binary)
        buffer_.seek(0)
        
        sys.stdout.write( '  %-75s' % query )
        try:
            result = buffer_reader.read(buffer_.getvalue()).data
            stream_reader = qreader.QReader(buffer_)
            result = stream_reader.read().data
            assert compare(value, result), 'deserialization failed: %s' % (query)
            print '.'
        except QException, e:
            assert isinstance(value, QException)
            assert e.message == value.message
            print '.'

        

test_reading()
test_reading_compressed()