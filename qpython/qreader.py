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

import struct
import sys

from qtype import *  # @UnusedWildImport
from qcollection import qlist, QDictionary, qtable, QTable, QKeyedTable
from qpython.qtemporal import qtemporallist, from_raw_qtemporal


class QReaderException(Exception):
    '''
    Indicates an error raised during data deserialization.
    '''
    pass



class QMessage(object):
    '''
    Represents a single message parsed from q protocol. Encapsulates data, message size, type etc.
    '''

    '''Parsed data.'''
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value


    '''Type of the message.'''
    @property
    def type(self):
        return self._type


    '''Indicates whether source message was compressed.'''
    @property
    def is_compressed(self):
        return self._is_compressed


    '''Size of the source message.'''
    @property
    def size(self):
        return self._size


    def __init__(self, data, message_type, message_size, is_compressed):
        self._data = data
        self._type = message_type
        self._size = message_size
        self._is_compressed = is_compressed




class QReader(object):
    '''
    Provides deserialization from q IPC protocol.
    '''

    reader_map = {}
    parse = Mapper(reader_map)

    def __init__(self, stream):
        self._stream = stream
        self._buffer = QReader.BytesBuffer()


    '''
    Reads and optionally parses a single message.

    Arguments:
    source -- optional buffer containing source to be read, if not specified data is read from the wrapped stream
    '''
    def read(self, source = None, raw = False):
        message = self.read_header(source)
        message.data = self.read_data(message.size, source, raw, message.is_compressed)

        return message


    ''' 
    Reads and parses message header.
    
    Arguments:
    source -- optional buffer containing source to be read, if not specified data is read from the wrapped stream
    '''
    def read_header(self, source = None):
        if self._stream:
            header = self._read_bytes(8)
            self._buffer.wrap(header)
        else:
            self._buffer.wrap(source)

        self._buffer.endianess = '<' if self._buffer.get_byte() == 1 else '>'
        self._is_native = self._buffer.endianess == ('<' if sys.byteorder == 'little' else '>')
        message_type = self._buffer.get_byte()
        message_compressed = self._buffer.get_byte() == 1
        # skip 1 byte
        self._buffer.skip()

        message_size = self._buffer.get_int()
        return QMessage(None, message_type, message_size, message_compressed)


    '''
    Reads and optionally parses data part of a message.

    Arguments:
    source -- optional buffer containing source to be read, if not specified data is read from the wrapped stream
    '''
    def read_data(self, message_size, source = None, raw = False, is_compressed = False):
        if is_compressed:
            if self._stream:
                self._buffer.wrap(self._read_bytes(4))

            uncompressed_size = -8 + self._buffer.get_int()
            compressed_data = self._read_bytes(message_size - 12) if self._stream else self._buffer.raw(message_size - 12)

            raw_data = self._uncompress(numpy.fromstring(compressed_data, dtype = numpy.uint8), numpy.int32(uncompressed_size))
            raw_data = numpy.ndarray.tostring(raw_data)
            self._buffer.wrap(raw_data)
        elif self._stream:
            raw_data = self._read_bytes(message_size - 8)
            self._buffer.wrap(raw_data)

        return raw_data if raw else self._read_object()

    def _uncompress(self, data, uncompressed_size):
        if  uncompressed_size <= 0:
            raise QReaderException('Error while data decompression.')

        _0 = numpy.int32(0)
        _1 = numpy.int32(1)
        _2 = numpy.int32(2)
        _128 = numpy.int32(128)
        _255 = numpy.int32(255)

        n, r, s, p, sn, pp, sp = _0, _0, _0, _0, _0, _0, _0
        i, d = _1, _1
        f = _255 & data[_0]

        ptrs = numpy.zeros(256, dtype = numpy.int32)
        uncompressed = numpy.zeros(uncompressed_size, dtype = numpy.uint8)

        while s < uncompressed_size:
            if (f & i) != _0:
                r = ptrs[_255 & data[d]]
                n = _2 + (_255 & data[d + _1])
                d += _2

                sn = s + n
                si = numpy.arange(s, sn)
                uncompressed[si] = uncompressed[r : r + n]

                pp = p + _1
                sp = s + _2
                while pp < sp:
                    ptrs[(_255 & uncompressed[p]) ^ (_255 & uncompressed[pp])] = p
                    p = pp
                    pp += _1

                s = sn
                p = s
            else:
                uncompressed[s] = data[d]

                s += _1
                d += _1

                pp = p + _1
                if pp < s:
                    ptrs[(_255 & uncompressed[p]) ^ (_255 & uncompressed[pp])] = p
                    p = pp

            if i == _128:
                if s < uncompressed_size:
                    f = _255 & data[d]
                    d += _1
                    i = _1
            else:
                i *= _2

        return uncompressed


    def _read_object(self):
        qtype = self._buffer.get_byte()

        reader = QReader.reader_map.get(qtype, None)

        if reader:
            return reader(self, qtype)
        elif qtype >= QBOOL_LIST and qtype <= QTIME_LIST:
            return self._read_list(qtype)
        elif qtype <= QBOOL and qtype >= QTIME:
            return self._read_atom(qtype)

        raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    @parse(QNULL)
    def _read_null(self, qtype = QNULL):
        return None


    @parse(QERROR)
    def _read_error(self, qtype = QERROR):
        raise QException(self._read_symbol())


    @parse(QSTRING)
    def _read_string(self, qtype = QSTRING):
        self._buffer.skip()  # ignore attributes
        length = self._buffer.get_int()
        return intern(self._buffer.raw(length)) if length > 0 else ''


    @parse(QSYMBOL)
    def _read_symbol(self, qtype = QSYMBOL):
        return numpy.string_(intern(self._buffer.get_symbol()))


    @parse(QCHAR)
    def _read_char(self, qtype = QCHAR):
        return chr(self._read_atom(QCHAR))


    @parse(QGUID)
    def _read_guid(self, qtype = QGUID):
        return uuid.UUID(bytes = self._buffer.raw(16))


    def _read_atom(self, qtype):
        try:
            fmt = STRUCT_MAP[qtype]
            conversion = FROM_Q[qtype]
            return conversion(self._buffer.get(fmt))
        except KeyError:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    @parse(QTIMESPAN, QTIMESTAMP, QTIME, QSECOND, QMINUTE, QDATE, QMONTH, QDATETIME)
    def _read_temporal(self, qtype):
        try:
            fmt = STRUCT_MAP[qtype]
            conversion = FROM_Q[qtype]
            return from_raw_qtemporal(conversion(self._buffer.get(fmt)), qtype = qtype)
        except KeyError:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    def _read_list(self, qtype):
        self._buffer.skip()  # ignore attributes
        length = self._buffer.get_int()
        conversion = FROM_Q.get(-qtype, None)

        if qtype == QSYMBOL_LIST:
            symbols = self._buffer.get_symbols(length)
            data = numpy.array(symbols, dtype = numpy.string_)

            return qlist(data, qtype = qtype, adjust_dtype = False)
        elif qtype >= QTIMESTAMP_LIST and qtype <= QTIME_LIST:
            raw = self._buffer.raw(length * ATOM_SIZE[qtype])
            data = numpy.fromstring(raw, dtype = conversion)
            if not self._is_native:
                data.byteswap(True)
            return qtemporallist(data, qtype = qtype, adjust_dtype = False)
        elif qtype == QGUID_LIST:
            data = numpy.array([self._read_guid() for x in xrange(length)])
            return qlist(data, qtype = qtype, adjust_dtype = False)
        elif conversion:
            raw = self._buffer.raw(length * ATOM_SIZE[qtype])
            data = numpy.fromstring(raw, dtype = conversion)
            if not self._is_native:
                data.byteswap(True)
            return qlist(data, qtype = qtype, adjust_dtype = False)
        else:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    @parse(QDICTIONARY)
    def _read_dictionary(self, qtype = QDICTIONARY):
        keys = self._read_object()
        values = self._read_object()

        if  isinstance(keys, QTable):
            return QKeyedTable(keys, values)
        else:
            return QDictionary(keys, values)


    @parse(QTABLE)
    def _read_table(self, qtype = QTABLE):
        self._buffer.skip()  # ignore attributes
        self._buffer.skip()  # ignore dict type stamp

        columns = self._read_object()
        data = self._read_object()

        return qtable(columns, data, qtype = QTABLE)


    @parse(QGENERAL_LIST)
    def _read_general_list(self, qtype = QGENERAL_LIST):
        self._buffer.skip()  # ignore attributes
        length = self._buffer.get_int()

        return [self._read_object() for x in xrange(length)]


    @parse(QLAMBDA)
    def _read_lambda(self, qtype = QLAMBDA):
        self._buffer.get_symbol()  # skip
        expression = self._read_object()
        return QLambda(expression)


    @parse(QLAMBDA_PART)
    def _read_lambda_part(self, qtype = QLAMBDA):
        length = self._buffer.get_int() - 1
        qlambda = self._read_lambda(qtype)
        qlambda.parameters = [ self._read_object() for x in range(length) ]
        return qlambda


    def _read_bytes(self, length):
        if not self._stream:
            raise QReaderException('There is no input data. QReader requires either stream or data chunk')

        if length == 0:
            return ''
        else:
            data = self._stream.read(length)

        if len(data) == 0:
            raise QReaderException('Error while reading data')
        return data



    class BytesBuffer(object):

        def __init__(self):
            self._endianess = '@'


        @property
        def endianess(self):
            return self._endianess


        @endianess.setter
        def endianess(self, endianess):
            self._endianess = endianess


        def wrap(self, data):
            self._data = data
            self._position = 0
            self._size = len(data)


        def skip(self, offset = 1):
            new_position = self._position + offset

            if new_position > self._size:
                raise QReaderException('Attempt to read data out of buffer bounds')

            self._position = new_position


        def raw(self, offset):
            new_position = self._position + offset

            if new_position > self._size:
                raise QReaderException('Attempt to read data out of buffer bounds')

            raw = self._data[self._position : new_position]
            self._position = new_position
            return raw


        def get(self, fmt, offset = None):
            fmt = self.endianess + fmt
            offset = offset if offset else struct.calcsize(fmt)
            return struct.unpack(fmt, self.raw(offset))[0]


        def get_byte(self):
            return self.get('b')


        def get_int(self):
            return self.get('i')


        def get_symbol(self):
            new_position = self._data.find('\x00', self._position)

            if new_position < 0:
                raise QReaderException('Failed to read symbol from stream')

            raw = self._data[self._position : new_position]
            self._position = new_position + 1
            return raw


        def get_symbols(self, size):
            count = 0
            new_position = self._position

            if size == 0:
                return []

            while count < size:
                new_position = self._data.find('\x00', new_position + 1)

                if new_position < 0:
                    raise QReaderException('Failed to read symbol from stream')

                count += 1

            raw = self._data[self._position : new_position]
            self._position = new_position + 1

            return raw.split('\x00')

