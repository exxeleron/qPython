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
import struct
import os
import sys
try:
    from cStringIO import BytesIO
except ImportError:
    from io import BytesIO

from collections import OrderedDict
from qpython import MetaData
from qpython._pandas import PandasQReader, PandasQWriter
from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import qlist, QList, QTemporalList, QDictionary
from qpython.qtemporal import QTemporal

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

try:
    import pandas
    BINARY = None

    PANDAS_EXPRESSIONS = OrderedDict((
                     (b'("G"$"8c680a01-5a49-5aab-5a65-d4bfddb6a661"; 0Ng)',
                                                                     {'data': pandas.Series(numpy.array([uuid.UUID('8c680a01-5a49-5aab-5a65-d4bfddb6a661'), numpy.nan])),
                                                                      'meta': MetaData(qtype = QGUID_LIST) }),
                     (b'"quick brown fox jumps over a lazy dog"',     b'quick brown fox jumps over a lazy dog'),
                     (b'" "',                                         b' '),
                     (b'``quick``fox',                                {'data': pandas.Series(numpy.array([qnull(QSYMBOL), numpy.string_('quick'), qnull(QSYMBOL), numpy.string_('fox')])),
                                                                      'meta': MetaData(qtype = QSYMBOL_LIST) }),
                     (b'`the`quick`brown`fox',                        {'data': pandas.Series(numpy.array([numpy.string_('the'), numpy.string_('quick'), numpy.string_('brown'), numpy.string_('fox')])),
                                                                      'meta': MetaData(qtype = QSYMBOL_LIST) }),
                     (b'("quick"; "brown"; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                       [b'quick', b'brown', b'fox', b'jumps', b'over', b'a lazy', b'dog']),
                     (b'("quick"; " "; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                       [b'quick', numpy.nan, b'fox', b'jumps', b'over', b'a lazy', b'dog']),

                     (b'(0b;1b;0b)',                                  {'data': pandas.Series(numpy.array([False, True, False], dtype = numpy.bool)),
                                                                      'meta': MetaData(qtype = QBOOL_LIST) }),
                     (b'(0x01;0x02;0xff)',                            {'data': pandas.Series(numpy.array([1, 2, 0xff], dtype = numpy.int8)),
                                                                      'meta': MetaData(qtype = QBYTE_LIST) }),
                     (b'(1h;2h;3h)',                                  {'data': pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int16)),
                                                                      'meta': MetaData(qtype = QSHORT_LIST) }),
                     (b'(1h;0Nh;3h)',                                 {'data': pandas.Series(numpy.array([1, numpy.nan, 3])),
                                                                      'meta': MetaData(qtype = QSHORT_LIST) }),
                     (b'1 2 3',                                       {'data': pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int64)),
                                                                      'meta': MetaData(qtype = QLONG_LIST) }),
                     (b'1 0N 3',                                      {'data': pandas.Series([1, numpy.nan, 3]),
                                                                      'meta': MetaData(qtype = QLONG_LIST) }),
                     (b'(1i;2i;3i)',                                  {'data': pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int32)),
                                                                      'meta': MetaData(qtype = QINT_LIST) }),
                     (b'(1i;0Ni;3i)',                                 {'data': pandas.Series(numpy.array([1, numpy.nan, 3])),
                                                                      'meta': MetaData(qtype = QINT_LIST) }),
                     (b'(1j;2j;3j)',                                  {'data': pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int64)),
                                                                      'meta': MetaData(qtype = QLONG_LIST) }),
                     (b'(1j;0Nj;3j)',                                 {'data': pandas.Series(numpy.array([1, numpy.nan, 3])),
                                                                      'meta': MetaData(qtype = QLONG_LIST) }),
                     (b'(5.5e; 8.5e)',                                {'data': pandas.Series(numpy.array([5.5, 8.5]), dtype = numpy.float32),
                                                                      'meta': MetaData(qtype = QFLOAT_LIST) }),
                     (b'(5.5e; 0Ne)',                                 {'data': pandas.Series(numpy.array([5.5, numpy.nan]), dtype = numpy.float32),
                                                                      'meta': MetaData(qtype = QFLOAT_LIST) }),
                     (b'3.23 6.46',                                   {'data': pandas.Series(numpy.array([3.23, 6.46])),
                                                                      'meta': MetaData(qtype = QDOUBLE_LIST) }),
                     (b'3.23 0n',                                     {'data': pandas.Series(numpy.array([3.23, numpy.nan])),
                                                                      'meta': MetaData(qtype = QDOUBLE_LIST) }),

                     (b'(2001.01m; 0Nm)',                             {'data': pandas.Series(numpy.array([numpy.datetime64('2001-01'), numpy.datetime64('NaT')], dtype='datetime64[M]')),
                                                                      'meta': MetaData(qtype = QMONTH_LIST) }),
                     (b'2001.01.01 2000.05.01 0Nd',                   {'data': pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]')),
                                                                      'meta': MetaData(qtype = QDATE_LIST) }),
                     (b'2000.01.04T05:36:57.600 0Nz',                 {'data': pandas.Series(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ms'), numpy.datetime64('nat', 'ms')])),
                                                                      'meta': MetaData(qtype = QDATETIME_LIST) }),
                     (b'12:01 0Nu',                                   {'data': pandas.Series(numpy.array([numpy.timedelta64(721, 'm'), numpy.timedelta64('nat', 'm')])),
                                                                      'meta': MetaData(qtype = QMINUTE_LIST) }),
                     (b'12:05:00 0Nv',                                {'data': pandas.Series(numpy.array([numpy.timedelta64(43500, 's'), numpy.timedelta64('nat', 's')])),
                                                                      'meta': MetaData(qtype = QSECOND_LIST) }),
                     (b'12:04:59.123 0Nt',                            {'data': pandas.Series(numpy.array([numpy.timedelta64(43499123, 'ms'), numpy.timedelta64('nat', 'ms')])),
                                                                      'meta': MetaData(qtype = QTIME_LIST) }),
                     (b'2000.01.04D05:36:57.600 0Np',                 {'data': pandas.Series(numpy.array([numpy.datetime64('2000-01-04T05:36:57.600Z', 'ns'), numpy.datetime64('nat', 'ns')])),
                                                                      'meta': MetaData(qtype = QTIMESTAMP_LIST) }),
                     (b'0D05:36:57.600 0Nn',                          {'data': pandas.Series(numpy.array([numpy.timedelta64(20217600000000, 'ns'), numpy.timedelta64('nat', 'ns')])),
                                                                      'meta': MetaData(qtype = QTIMESPAN_LIST) }),

                     (b'1 2!`abc`cdefgh',                             QDictionary(qlist(numpy.array([1, 2], dtype=numpy.int64), qtype=QLONG_LIST),
                                                                                 qlist(numpy.array(['abc', 'cdefgh']), qtype = QSYMBOL_LIST))),
                     (b'(0 1; 2 3)!`first`second',                    QDictionary([qlist(numpy.array([0, 1], dtype=numpy.int64), qtype=QLONG_LIST), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST)],
                                                                                  qlist(numpy.array(['first', 'second']), qtype = QSYMBOL_LIST))),
                     (b'(1;2h;3.234;"4")!(`one;2 3;"456";(7;8 9))',   QDictionary([numpy.int64(1), numpy.int16(2), numpy.float64(3.234), b'4'],
                                                                                 [numpy.string_('one'), qlist(numpy.array([2, 3], dtype=numpy.int64), qtype=QLONG_LIST), b'456', [numpy.int64(7), qlist(numpy.array([8, 9], dtype=numpy.int64), qtype=QLONG_LIST)]])),
                     (b'`A`B`C!((1;3.234;3);(`x`y!(`a;2));5.5e)',     QDictionary(qlist(numpy.array(['A', 'B', 'C']), qtype = QSYMBOL_LIST),
                                                                                 [[numpy.int64(1), numpy.float64(3.234), numpy.int64(3)], QDictionary(qlist(numpy.array(['x', 'y']), qtype = QSYMBOL_LIST), [numpy.string_('a'), numpy.int64(2)]), numpy.float32(5.5)])),

                     (b'flip `abc`def!(1 2 3; 4 5 6)',                {'data': pandas.DataFrame(OrderedDict((('abc', pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int64))),
                                                                                                            ('def', pandas.Series(numpy.array([4, 5, 6], dtype = numpy.int64)))))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'abc': QLONG_LIST, 'def': QLONG_LIST}) }),
                     (b'flip `name`iq!(`Dent`Beeblebrox`Prefect;98 42 126)',
                                                                     {'data': pandas.DataFrame(OrderedDict((('name', pandas.Series(['Dent', 'Beeblebrox', 'Prefect'], dtype = numpy.string_)),
                                                                                                            ('iq', pandas.Series(numpy.array([98, 42, 126], dtype = numpy.int64)))))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'name': QSYMBOL_LIST, 'iq': QLONG_LIST}) }),
                     (b'flip `name`iq`grade!(`Dent`Beeblebrox`Prefect;98 42 126;"a c")',
                                                                     {'data': pandas.DataFrame(OrderedDict((('name', pandas.Series(['Dent', 'Beeblebrox', 'Prefect'], dtype = numpy.string_)),
                                                                                                            ('iq', pandas.Series(numpy.array([98, 42, 126], dtype = numpy.int64))),
                                                                                                            ('grade', pandas.Series(['a', ' ', 'c'], dtype = numpy.str).replace(b' ', numpy.nan)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'name': QSYMBOL_LIST, 'iq': QLONG_LIST, 'grade': QSTRING}) }),
                     (b'1#([] sym:`x`x`x;str:"  a")',
                                                                     {'data': pandas.DataFrame(OrderedDict((('sym', pandas.Series(['x'], dtype = numpy.string_)),
                                                                                                            ('str', pandas.Series([' '], dtype = numpy.str).replace(b' ', numpy.nan)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'sym': QSYMBOL_LIST, 'str': QSTRING}),
                                                                      'single_char_strings': True}),
                     (b'-1#([] sym:`x`x`x;str:"  a")',
                                                                     {'data': pandas.DataFrame(OrderedDict((('sym', pandas.Series(['x'], dtype = numpy.string_)),
                                                                                                            ('str', pandas.Series(['a'], dtype = numpy.str)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'sym': QSYMBOL_LIST, 'str': QSTRING}),
                                                                      'single_char_strings': True}),
                     (b'2#([] sym:`x`x`x`x;str:"  aa")',
                                                                     {'data': pandas.DataFrame(OrderedDict((('sym', pandas.Series(['x', 'x'], dtype = numpy.string_)),
                                                                                                            ('str', pandas.Series([' ', ' '], dtype = numpy.str).replace(b' ', numpy.nan)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'sym': QSYMBOL_LIST, 'str': QSTRING})}),
                     (b'-2#([] sym:`x`x`x`x;str:"  aa")',
                                                                     {'data': pandas.DataFrame(OrderedDict((('sym', pandas.Series(['x', 'x'], dtype = numpy.string_)),
                                                                                                            ('str', pandas.Series(['a', 'a'], dtype = numpy.str).replace(b' ', numpy.nan)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'sym': QSYMBOL_LIST, 'str': QSTRING})}),
                     (b'flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; "Zaphod Beeblebrox"; "Ford Prefect"))',
                                                                     {'data': pandas.DataFrame(OrderedDict((('name', pandas.Series(['Dent', 'Beeblebrox', 'Prefect'], dtype = numpy.string_)),
                                                                                                            ('iq', pandas.Series(numpy.array([98, 42, 126], dtype = numpy.int64))),
                                                                                                            ('fullname', pandas.Series(["Arthur Dent", "Zaphod Beeblebrox", "Ford Prefect"], dtype = numpy.string_)),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'name': QSYMBOL_LIST, 'iq': QLONG_LIST, 'fullname': QSTRING_LIST}) }),
                     (b'flip `name`iq`fullname!(`Dent`Beeblebrox`Prefect;98 42 126;("Arthur Dent"; " "; "Ford Prefect"))',
                                                                     {'data': pandas.DataFrame(OrderedDict((('name', pandas.Series(['Dent', 'Beeblebrox', 'Prefect'], dtype = numpy.string_)),
                                                                                                            ('iq', pandas.Series(numpy.array([98, 42, 126], dtype = numpy.int64))),
                                                                                                            ('fullname', pandas.Series([b"Arthur Dent", numpy.nan, b"Ford Prefect"])),
                                                                                                             ))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'name': QSYMBOL_LIST, 'iq': QLONG_LIST, 'fullname': QSTRING_LIST}) }),
                     (b'([] sc:1 2 3; nsc:(1 2; 3 4; 5 6 7))',        {'data': pandas.DataFrame(OrderedDict((('sc', pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int64))),
                                                                                                            ('nsc', [pandas.Series(numpy.array([1, 2], dtype = numpy.int64)), pandas.Series(numpy.array([3, 4], dtype = numpy.int64)), pandas.Series(numpy.array([5, 6, 7], dtype = numpy.int64))])))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'nsc': QGENERAL_LIST, 'sc': QLONG_LIST}) }),
                     (b'([] sc:1 2 3; nsc:(1 2; 3 4; 5 6))',          {'data': pandas.DataFrame(OrderedDict((('sc', pandas.Series(numpy.array([1, 2, 3], dtype = numpy.int64))),
                                                                                                            ('nsc', [pandas.Series(numpy.array([1, 2], dtype = numpy.int64)), pandas.Series(numpy.array([3, 4], dtype = numpy.int64)), pandas.Series(numpy.array([5, 6], dtype = numpy.int64))])))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'nsc': QGENERAL_LIST, 'sc': QLONG_LIST}) }),
                     (b'([] name:`symbol$(); iq:`int$())',            {'data': pandas.DataFrame(OrderedDict((('name', pandas.Series(numpy.array([], dtype = numpy.string_))),
                                                                                                            ('iq', pandas.Series(numpy.array([], dtype = numpy.int32)))))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'name': QSYMBOL_LIST, 'iq': QINT_LIST}) }),
                     (b'([] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                     {'data': pandas.DataFrame(OrderedDict((('pos', pandas.Series(numpy.array(['d1', 'd2', 'd3'], dtype = numpy.string_))),
                                                                                                            ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]')))))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QTABLE, 'pos': QSYMBOL_LIST, 'dates': QDATE_LIST}) }),
                     (b'([eid:1001 1002 1003] pos:`d1`d2`d3;dates:(2001.01.01;2000.05.01;0Nd))',
                                                                     {'data': pandas.DataFrame(OrderedDict((('eid', pandas.Series(numpy.array([1001, 1002, 1003], dtype = numpy.int64))),
                                                                                                            ('pos', pandas.Series(numpy.array(['d1', 'd2', 'd3'], dtype = numpy.string_))),
                                                                                                            ('dates', pandas.Series(numpy.array([numpy.datetime64('2001-01-01'), numpy.datetime64('2000-05-01'), numpy.datetime64('NaT')], dtype='datetime64[D]')))))
                                                                                               ),
                                                                      'meta': MetaData(**{'qtype': QKEYED_TABLE, 'pos': QSYMBOL_LIST, 'dates': QDATE_LIST, 'eid': QLONG_LIST}),
                                                                      'index': ['eid'] }),
                     (b'([k: 1 2 3] v: `a`b`c)',
                                                                     {'data': pandas.DataFrame({'k':numpy.array([1, 2, 3], dtype = numpy.int64),'v':numpy.array(['a', 'b', 'c'], dtype = numpy.string_)}),
                                                                      'meta': MetaData(**{'qtype': QKEYED_TABLE}),
                                                                      'index': ['k'],
                                                                      'compare_meta': False }),
                                    ))


    PANDAS_EXPRESSIONS_ALT = OrderedDict((
                     (b'("quick"; "brown"; "fox"; "jumps"; "over"; "a lazy"; "dog")',
                                                                     {'data': pandas.Series(['quick', 'brown', 'fox', 'jumps', 'over', 'a lazy', 'dog']),
                                                                      'meta': MetaData(qtype = QSTRING_LIST) }),
                                       ))

    def arrays_equal(left, right):
        if type(left) != type(right):
            return False

        if type(left) in [numpy.ndarray, pandas.Series] and left.dtype.type != right.dtype.type:
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
                print('Value comparison failed: %s != %s' % (left[i], right[i]))
                return False

        return True


    def compare(left, right):
        if type(left) in [float, numpy.float32, numpy.float64] and numpy.isnan(left):
            return numpy.isnan(right)
        if type(left) == QTemporal and isinstance(left.raw, float) and numpy.isnan(left.raw):
            return numpy.isnan(right.raw)
        elif type(left) in [list, tuple, numpy.ndarray, QList, QTemporalList, pandas.Series]:
            return arrays_equal(left, right)
        elif type(left) == pandas.DataFrame:
            for c in left:
                if not arrays_equal(left[c], right[c]):
                    return False

            return True
        elif type(left) == QFunction:
            return type(right) == QFunction
        elif pandas.isnull(left):
            return pandas.isnull(right)
        else:
            return left == right


    def init():
        global BINARY
        BINARY = OrderedDict()

        with open(os.path.join(TEST_DATA_DIR, 'QExpressions3.out'), 'rb') as f:
            while True:
                query = f.readline().strip()
                binary = f.readline().strip()

                if not binary:
                    break

                BINARY[query] = binary


    def test_reading_pandas():
        print('Deserialization (pandas)')
        for query, value in iter(PANDAS_EXPRESSIONS.items()):
            buffer_ = BytesIO()
            binary = binascii.unhexlify(BINARY[query])

            buffer_.write(b'\1\0\0\0')
            buffer_.write(struct.pack('i', len(binary) + 8))
            buffer_.write(binary)
            buffer_.seek(0)

            sys.stdout.write('  %-75s' % query)
            try:
                buffer_.seek(0)
                stream_reader = PandasQReader(buffer_)
                result = stream_reader.read(pandas = True).data
                if isinstance(value, dict):
                    if 'index' in value:
                        meta = result.meta
                        result = result.reset_index()
                        result.meta = meta

                    if not 'compare_meta' in value or value['compare_meta']:
                        assert value['meta'].as_dict() == result.meta.as_dict(), 'deserialization failed qtype: %s, expected: %s actual: %s' % (query, value['meta'], result.meta)
                    assert compare(value['data'], result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value['data'], result)
                else:
                    assert compare(value, result), 'deserialization failed: %s, expected: %s actual: %s' % (query, value, result)
                print('.')
            except QException as e:
                assert isinstance(value, QException)
                assert e.message == value.message
                print('.')


    def test_writing_pandas():
        w = PandasQWriter(None, 3)

        for query, value in iter(PANDAS_EXPRESSIONS.items()):
            sys.stdout.write( '%-75s' % query )
            single_char_strings = False
            if isinstance(value, dict):
                data = value['data']
                if 'index' in value:
                    data = data.reset_index(drop = True)
                    data = data.set_index(value['index'])
                if 'single_char_strings' in value:
                    single_char_strings = value['single_char_strings']
                data.meta = value['meta']
            else:
                data = value
            serialized = binascii.hexlify(w.write(data, 1, single_char_strings = single_char_strings, pandas = True))[16:].lower()
            assert serialized == BINARY[query].lower(), 'serialization failed: %s, expected: %s actual: %s' % (value,  BINARY[query].lower(), serialized)
            sys.stdout.write( '.' )

            print('')

        for query, value in iter(PANDAS_EXPRESSIONS_ALT.items()):
            sys.stdout.write( '%-75s' % query )
            if isinstance(value, dict):
                data = value['data']
                if 'index' in value:
                    data.reset_index(drop = True)
                    data = data.set_index(value['index'])
                data.meta = value['meta']
            else:
                data = value
            serialized = binascii.hexlify(w.write(data, 1))[16:].lower()
            assert serialized == BINARY[query].lower(), 'serialization failed: %s, expected: %s actual: %s' % (value,  BINARY[query].lower(), serialized)
            sys.stdout.write( '.' )

            print('')


    init()
    test_reading_pandas()
    test_writing_pandas()
except ImportError:
    pandas = None
