#
#  Copyright (c) 2011-2016 Exxeleron GmbH
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

import numpy

from qpython import qconnection
from qpython.qreader import QReader
from qpython.qtype import QSYMBOL, QSYMBOL_LIST, Mapper


class StringQReader(QReader):
    # QReader and QWriter use decorators to map data types and corresponding function handlers
    _reader_map = dict.copy(QReader._reader_map)
    parse = Mapper(_reader_map)

    def _read_list(self, qtype):
        if qtype == QSYMBOL_LIST:
            self._buffer.skip()
            length = self._buffer.get_int()
            symbols = self._buffer.get_symbols(length)
            return [s.decode(self._encoding) for s in symbols]
        else:
            return QReader._read_list(self, qtype = qtype)

    @parse(QSYMBOL)
    def _read_symbol(self, qtype = QSYMBOL):
        return numpy.string_(self._buffer.get_symbol()).decode(self._encoding)



class ReverseStringQReader(QReader):
    # QReader and QWriter use decorators to map data types and corresponding function handlers
    _reader_map = dict.copy(QReader._reader_map)
    parse = Mapper(_reader_map)

    @parse(QSYMBOL_LIST)
    def _read_symbol_list(self, qtype):
        self._buffer.skip()
        length = self._buffer.get_int()
        symbols = self._buffer.get_symbols(length)
        return [s.decode(self._encoding)[::-1] for s in symbols]

    @parse(QSYMBOL)
    def _read_symbol(self, qtype = QSYMBOL):
        return numpy.string_(self._buffer.get_symbol()).decode(self._encoding)[::-1]



if __name__ == '__main__':
    with qconnection.QConnection(host = 'localhost', port = 5000, reader_class = StringQReader) as q:
        symbols = q.sendSync('`foo`bar')
        print(symbols, type(symbols), type(symbols[0]))
    
        symbol = q.sendSync('`foo')
        print(symbol, type(symbol))
    
    
    with qconnection.QConnection(host = 'localhost', port = 5000, reader_class = ReverseStringQReader) as q:
        symbols = q.sendSync('`foo`bar')
        print(symbols, type(symbols), type(symbols[0]))
    
        symbol = q.sendSync('`foo')
        print(symbol, type(symbol))
