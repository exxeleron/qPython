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
if sys.version > '3':
    from sys import intern
    unicode = str

from qpython import MetaData, CONVERSION_OPTIONS
from qpython.qtype import *  # @UnusedWildImport
from qpython.qcollection import qlist, QDictionary, qtable, QTable, QKeyedTable
from qpython.qtemporal import qtemporal, from_raw_qtemporal, array_from_raw_qtemporal

try:
    from qpython.fastutils import uncompress
except:
    from qpython.utils import uncompress



class QReaderException(Exception):
    '''
    Indicates an error raised during data deserialization.
    '''
    pass



class QMessage(object):
    '''
    Represents a single message parsed from q protocol. 
    Encapsulates data, message size, type, compression flag.
    
    :Parameters:
     - `data` - data payload
     - `message_type` (one of the constants defined in :class:`.MessageType`) -
       type of the message
     - `message_size` (`integer`) - size of the message
     - `is_compressed` (`boolean`) - indicates whether message is compressed
    '''

    @property
    def data(self):
        '''Parsed data.'''
        return self._data

    @data.setter
    def data(self, value):
        self._data = value


    @property
    def type(self):
        '''Type of the message.'''
        return self._type


    @property
    def is_compressed(self):
        '''Indicates whether source message was compressed.'''
        return self._is_compressed


    @property
    def size(self):
        '''Size of the source message.'''
        return self._size


    def __init__(self, data, message_type, message_size, is_compressed):
        self._data = data
        self._type = message_type
        self._size = message_size
        self._is_compressed = is_compressed


    def __str__(self, *args, **kwargs):
        return 'QMessage: message type: %s, data size: %s, is_compressed: %s, data: %s' % (self._type, self._size, self._is_compressed, self._data)



class QReader(object):
    '''
    Provides deserialization from q IPC protocol.
    
    :Parameters:
     - `stream` (`file object` or `None`) - data input stream
     - `encoding` (`string`) - encoding for characters parsing
     
    :Attrbutes:
     - `_reader_map` - stores mapping between q types and functions 
       responsible for parsing into Python objects    
    '''

    _reader_map = {}
    parse = Mapper(_reader_map)


    def __init__(self, stream, encoding = 'latin-1'):
        self._stream = stream
        self._buffer = QReader.BytesBuffer()
        self._encoding = encoding


    def read(self, source = None, **options):
        '''
        Reads and optionally parses a single message.
        
        :Parameters:
         - `source` - optional data buffer to be read, if not specified data is 
           read from the wrapped stream
        :Options:
         - `raw` (`boolean`) - indicates whether read data should parsed or 
           returned in raw byte form
         - `numpy_temporals` (`boolean`) - if ``False`` temporal vectors are
           backed by raw q representation (:class:`.QTemporalList`, 
           :class:`.QTemporal`) instances, otherwise are represented as 
           `numpy datetime64`/`timedelta64` arrays and atoms,
           **Default**: ``False``
         
        :returns: :class:`.QMessage` - read data (parsed or raw byte form) along
                  with meta information
        '''
        message = self.read_header(source)
        message.data = self.read_data(message.size, message.is_compressed, **options)

        return message


    def read_header(self, source = None):
        '''
        Reads and parses message header.
        
        .. note:: :func:`.read_header` wraps data for further reading in internal
                  buffer  
    
        :Parameters:
         - `source` - optional data buffer to be read, if not specified data is 
           read from the wrapped stream
           
        :returns: :class:`.QMessage` - read meta information
        '''
        if self._stream:
            header = self._read_bytes(8)
            self._buffer.wrap(header)
        else:
            self._buffer.wrap(source)

        self._buffer.endianness = '<' if self._buffer.get_byte() == 1 else '>'
        self._is_native = self._buffer.endianness == ('<' if sys.byteorder == 'little' else '>')
        message_type = self._buffer.get_byte()
        message_compressed = self._buffer.get_byte() == 1
        # skip 1 byte
        self._buffer.skip()

        message_size = self._buffer.get_int()
        return QMessage(None, message_type, message_size, message_compressed)


    def read_data(self, message_size, is_compressed = False, **options):
        '''
        Reads and optionally parses data part of a message.
        
        .. note:: :func:`.read_header` is required to be called before executing
                  the :func:`.read_data`
        
        :Parameters:
         - `message_size` (`integer`) - size of the message to be read
         - `is_compressed` (`boolean`) - indicates whether data is compressed
        :Options:
         - `raw` (`boolean`) - indicates whether read data should parsed or 
           returned in raw byte form
         - `numpy_temporals` (`boolean`) - if ``False`` temporal vectors are
           backed by raw q representation (:class:`.QTemporalList`, 
           :class:`.QTemporal`) instances, otherwise are represented as 
           `numpy datetime64`/`timedelta64` arrays and atoms,
           **Default**: ``False``
         
        :returns: read data (parsed or raw byte form)
        '''
        self._options = MetaData(**CONVERSION_OPTIONS.union_dict(**options))

        if is_compressed:
            if self._stream:
                self._buffer.wrap(self._read_bytes(4))
            uncompressed_size = -8 + self._buffer.get_int()
            compressed_data = self._read_bytes(message_size - 12) if self._stream else self._buffer.raw(message_size - 12)

            raw_data = numpy.fromstring(compressed_data, dtype = numpy.uint8)
            if  uncompressed_size <= 0:
                raise QReaderException('Error while data decompression.')

            raw_data = uncompress(raw_data, numpy.intc(uncompressed_size))
            raw_data = numpy.ndarray.tostring(raw_data)
            self._buffer.wrap(raw_data)
        elif self._stream:
            raw_data = self._read_bytes(message_size - 8)
            self._buffer.wrap(raw_data)
        if not self._stream and self._options.raw:
            raw_data = self._buffer.raw(message_size - 8)

        return raw_data if self._options.raw else self._read_object()


    def _read_object(self):
        qtype = self._buffer.get_byte()

        reader = self._get_reader(qtype)

        if reader:
            return reader(self, qtype)
        elif qtype >= QBOOL_LIST and qtype <= QTIME_LIST:
            return self._read_list(qtype)
        elif qtype <= QBOOL and qtype >= QTIME:
            return self._read_atom(qtype)

        raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    def _get_reader(self, qtype):
        return self._reader_map.get(qtype, None)


    @parse(QERROR)
    def _read_error(self, qtype = QERROR):
        raise QException(self._read_symbol())


    @parse(QSTRING)
    def _read_string(self, qtype = QSTRING):
        self._buffer.skip()  # ignore attributes
        length = self._buffer.get_int()
        return self._buffer.raw(length) if length > 0 else b''


    @parse(QSYMBOL)
    def _read_symbol(self, qtype = QSYMBOL):
        return numpy.string_(self._buffer.get_symbol())


    @parse(QCHAR)
    def _read_char(self, qtype = QCHAR):
        return chr(self._read_atom(QCHAR)).encode(self._encoding)


    @parse(QGUID)
    def _read_guid(self, qtype = QGUID):
        return uuid.UUID(bytes = self._buffer.raw(16))


    def _read_atom(self, qtype):
        try:
            fmt = STRUCT_MAP[qtype]
            conversion = PY_TYPE[qtype]
            return conversion(self._buffer.get(fmt))
        except KeyError:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    @parse(QTIMESPAN, QTIMESTAMP, QTIME, QSECOND, QMINUTE, QDATE, QMONTH, QDATETIME)
    def _read_temporal(self, qtype):
        try:
            fmt = STRUCT_MAP[qtype]
            conversion = PY_TYPE[qtype]
            temporal = from_raw_qtemporal(conversion(self._buffer.get(fmt)), qtype = qtype)
            return temporal if self._options.numpy_temporals else qtemporal(temporal, qtype = qtype)
        except KeyError:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    def _read_list(self, qtype):
        self._buffer.skip()  # ignore attributes
        length = self._buffer.get_int()
        conversion = PY_TYPE.get(-qtype, None)

        if qtype == QSYMBOL_LIST:
            symbols = self._buffer.get_symbols(length)
            data = numpy.array(symbols, dtype = numpy.string_)
            return qlist(data, qtype = qtype, adjust_dtype = False)
        elif qtype == QGUID_LIST:
            data = numpy.array([self._read_guid() for x in range(length)])
            return qlist(data, qtype = qtype, adjust_dtype = False)
        elif conversion:
            raw = self._buffer.raw(length * ATOM_SIZE[qtype])
            data = numpy.fromstring(raw, dtype = conversion)
            if not self._is_native:
                data.byteswap(True)

            if qtype >= QTIMESTAMP_LIST and qtype <= QTIME_LIST and self._options.numpy_temporals:
                data = array_from_raw_qtemporal(data, qtype)

            return qlist(data, qtype = qtype, adjust_dtype = False)
        else:
            raise QReaderException('Unable to deserialize q type: %s' % hex(qtype))


    @parse(QDICTIONARY)
    def _read_dictionary(self, qtype = QDICTIONARY):
        keys = self._read_object()
        values = self._read_object()

        if isinstance(keys, QTable):
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

        return [self._read_object() for x in range(length)]


    @parse(QNULL)
    @parse(QUNARY_FUNC)
    @parse(QBINARY_FUNC)
    @parse(QTERNARY_FUNC)
    def _read_function(self, qtype = QNULL):
        code = self._buffer.get_byte()
        return None if qtype == QNULL and code == 0 else QFunction(qtype)


    @parse(QLAMBDA)
    def _read_lambda(self, qtype = QLAMBDA):
        self._buffer.get_symbol()  # skip
        expression = self._read_object()
        return QLambda(expression.decode())


    @parse(QCOMPOSITION_FUNC)
    def _read_function_composition(self, qtype = QCOMPOSITION_FUNC):
        self._read_projection(qtype)  # skip
        return QFunction(qtype)


    @parse(QADVERB_FUNC_106)
    @parse(QADVERB_FUNC_107)
    @parse(QADVERB_FUNC_108)
    @parse(QADVERB_FUNC_109)
    @parse(QADVERB_FUNC_110)
    @parse(QADVERB_FUNC_111)
    def _read_adverb_function(self, qtype = QADVERB_FUNC_106):
        self._read_object()  # skip
        return QFunction(qtype)


    @parse(QPROJECTION)
    def _read_projection(self, qtype = QPROJECTION):
        length = self._buffer.get_int()
        parameters = [ self._read_object() for x in range(length) ]
        return QProjection(parameters)


    def _read_bytes(self, length):
        if not self._stream:
            raise QReaderException('There is no input data. QReader requires either stream or data chunk')

        if length == 0:
            return b''
        else:
            data = self._stream.read(length)

        if len(data) == 0:
            raise QReaderException('Error while reading data')
        return data



    class BytesBuffer(object):
        '''
        Utility class for reading bytes from wrapped buffer.
        '''

        def __init__(self):
            self._endianness = '@'


        @property
        def endianness(self):
            '''
            Gets the endianness.
            '''
            return self._endianness


        @endianness.setter
        def endianness(self, endianness):
            '''
            Sets the byte order (endianness) for reading from the buffer.
            
            :Parameters:
             - `endianness` (``<`` or ``>``) - byte order indicator
            '''
            self._endianness = endianness


        def wrap(self, data):
            '''
            Wraps the data in the buffer.
            
            :Parameters:
             - `data` - data to be wrapped
            '''
            self._data = data
            self._position = 0
            self._size = len(data)


        def skip(self, offset = 1):
            '''
            Skips reading of `offset` bytes.
            
            :Parameters:
             - `offset` (`integer`) - number of bytes to be skipped
            '''
            new_position = self._position + offset

            if new_position > self._size:
                raise QReaderException('Attempt to read data out of buffer bounds')

            self._position = new_position


        def raw(self, offset):
            '''
            Gets `offset` number of raw bytes.
            
            :Parameters:
             - `offset` (`integer`) - number of bytes to be retrieved
             
            :returns: raw bytes
            '''
            new_position = self._position + offset

            if new_position > self._size:
                raise QReaderException('Attempt to read data out of buffer bounds')

            raw = self._data[self._position : new_position]
            self._position = new_position
            return raw


        def get(self, fmt, offset = None):
            '''
            Gets bytes from the buffer according to specified format or `offset`.
            
            :Parameters:
             - `fmt` (struct format) - conversion to be applied for reading
             - `offset` (`integer`) - number of bytes to be retrieved
            
            :returns: unpacked bytes
            '''
            fmt = self.endianness + fmt
            offset = offset if offset else struct.calcsize(fmt)
            return struct.unpack(fmt, self.raw(offset))[0]


        def get_byte(self):
            '''
            Gets a single byte from the buffer.
            
            :returns: single byte
            '''
            return self.get('b')


        def get_int(self):
            '''
            Gets a single 32-bit integer from the buffer.
            
            :returns: single integer
            '''
            return self.get('i')


        def get_symbol(self):
            '''
            Gets a single, ``\\x00`` terminated string from the buffer.
            
            :returns: ``\\x00`` terminated string
            '''
            new_position = self._data.find(b'\x00', self._position)

            if new_position < 0:
                raise QReaderException('Failed to read symbol from stream')

            raw = self._data[self._position : new_position]
            self._position = new_position + 1
            return raw


        def get_symbols(self, count):
            '''
            Gets ``count`` ``\\x00`` terminated strings from the buffer.
            
            :Parameters:
             - `count` (`integer`) - number of strings to be read
            
            :returns: list of ``\\x00`` terminated string read from the buffer
            '''
            c = 0
            new_position = self._position

            if count == 0:
                return []

            while c < count:
                new_position = self._data.find(b'\x00', new_position)

                if new_position < 0:
                    raise QReaderException('Failed to read symbol from stream')

                c += 1
                new_position += 1

            raw = self._data[self._position : new_position - 1]
            self._position = new_position

            return raw.split(b'\x00')


