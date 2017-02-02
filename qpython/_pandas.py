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

import pandas
import struct
import sys
if sys.version > '3':
    basestring = (str, bytes)

from collections import OrderedDict

from qpython import MetaData
from qpython.qreader import QReader, QReaderException
from qpython.qcollection import QDictionary, qlist
from qpython.qwriter import QWriter, QWriterException
from qpython.qtype import *



class PandasQReader(QReader):

    _reader_map = dict.copy(QReader._reader_map)
    parse = Mapper(_reader_map)

    @parse(QDICTIONARY)
    def _read_dictionary(self, qtype = QDICTIONARY):
        if self._options.pandas:
            keys = self._read_object()
            values = self._read_object()

            if isinstance(keys, pandas.DataFrame):
                if not isinstance(values, pandas.DataFrame):
                    raise QReaderException('Keyed table creation: values are expected to be of type pandas.DataFrame. Actual: %s' % type(values))

                indices = keys.columns
                table = keys
                table.meta = keys.meta
                table.meta.qtype = QKEYED_TABLE

                for column in values.columns:
                    table[column] = values[column]
                    table.meta[column] = values.meta[column]

                table.set_index([column for column in indices], inplace = True)

                return table
            else:
                keys = keys if not isinstance(keys, pandas.Series) else keys.as_matrix()
                values = values if not isinstance(values, pandas.Series) else values.as_matrix()
                return QDictionary(keys, values)
        else:
            return QReader._read_dictionary(self, qtype = qtype)


    @parse(QTABLE)
    def _read_table(self, qtype = QTABLE):
        if self._options.pandas:
            self._buffer.skip()  # ignore attributes
            self._buffer.skip()  # ignore dict type stamp

            columns = self._read_object()
            self._buffer.skip() # ignore generic list type indicator
            data = QReader._read_general_list(self, qtype)

            odict = OrderedDict()
            meta = MetaData(qtype = QTABLE)
            for i in range(len(columns)):
                column_name = columns[i] if isinstance(columns[i], str) else columns[i].decode("utf-8")
                if isinstance(data[i], str):
                    # convert character list (represented as string) to numpy representation
                    meta[column_name] = QSTRING
                    odict[column_name] = pandas.Series(list(data[i]), dtype = numpy.str).replace(b' ', numpy.nan)
                elif isinstance(data[i], bytes):
                    # convert character list (represented as string) to numpy representation
                    meta[column_name] = QSTRING
                    odict[column_name] = pandas.Series(list(data[i].decode()), dtype = numpy.str).replace(b' ', numpy.nan)
                elif isinstance(data[i], (list, tuple)):
                    meta[column_name] = QGENERAL_LIST
                    tarray = numpy.ndarray(shape = len(data[i]), dtype = numpy.dtype('O'))
                    for j in range(len(data[i])):
                        tarray[j] = data[i][j]
                    odict[column_name] = tarray
                else:
                    meta[column_name] = data[i].meta.qtype
                    odict[column_name] = data[i]

            df = pandas.DataFrame(odict)
            df.meta = meta
            return df
        else:
            return QReader._read_table(self, qtype = qtype)


    def _read_list(self, qtype):
        if self._options.pandas:
            self._options.numpy_temporals = True

        qlist = QReader._read_list(self, qtype = qtype)

        if self._options.pandas:
            if -abs(qtype) not in [QMONTH, QDATE, QDATETIME, QMINUTE, QSECOND, QTIME, QTIMESTAMP, QTIMESPAN, QSYMBOL]:
                null = QNULLMAP[-abs(qtype)][1]
                ps = pandas.Series(data = qlist).replace(null, numpy.NaN)
            else:
                ps = pandas.Series(data = qlist)

            ps.meta = MetaData(qtype = qtype)
            return ps
        else:
            return qlist


    @parse(QGENERAL_LIST)
    def _read_general_list(self, qtype = QGENERAL_LIST):
        qlist = QReader._read_general_list(self, qtype)
        if self._options.pandas:
            return [numpy.nan if isinstance(element, basestring) and element == b' ' else element for element in qlist]
        else:
            return qlist



class PandasQWriter(QWriter):

    _writer_map = dict.copy(QWriter._writer_map)
    serialize = Mapper(_writer_map)


    @serialize(pandas.Series)
    def _write_pandas_series(self, data, qtype = None):
        if qtype is not None:
            qtype = -abs(qtype)

        if qtype is None and hasattr(data, 'meta'):
            qtype = -abs(data.meta.qtype)

        if data.dtype == '|S1':
            qtype = QCHAR

        if qtype is None:
            qtype = Q_TYPE.get(data.dtype.type, None)

        if qtype is None and data.dtype.type in (numpy.datetime64, numpy.timedelta64):
            qtype = TEMPORAL_PY_TYPE.get(str(data.dtype), None)

        if qtype is None:
            # determinate type based on first element of the numpy array
            qtype = Q_TYPE.get(type(data.iloc[0]), QGENERAL_LIST)

            if qtype == QSTRING:
                # assume we have a generic list of strings -> force representation as symbol list
                qtype = QSYMBOL

        if qtype is None:
            raise QWriterException('Unable to serialize pandas series %s' % data)

        if qtype == QGENERAL_LIST:
            self._write_generic_list(data.as_matrix())
        elif qtype == QCHAR:
            self._write_string(data.replace(numpy.nan, ' ').as_matrix().astype(numpy.string_).tostring())
        elif data.dtype.type not in (numpy.datetime64, numpy.timedelta64):
            data = data.fillna(QNULLMAP[-abs(qtype)][1])
            data = data.as_matrix()

            if PY_TYPE[qtype] != data.dtype:
                data = data.astype(PY_TYPE[qtype])

            self._write_list(data, qtype = qtype)
        else:
            data = data.as_matrix()
            data = data.astype(TEMPORAL_Q_TYPE[qtype])
            self._write_list(data, qtype = qtype)


    @serialize(pandas.DataFrame)
    def _write_pandas_data_frame(self, data, qtype = None):
        data_columns = data.columns.values

        if hasattr(data, 'meta') and data.meta.qtype == QKEYED_TABLE:
            # data frame represents keyed table
            self._buffer.write(struct.pack('=b', QDICTIONARY))
            self._buffer.write(struct.pack('=bxb', QTABLE, QDICTIONARY))
            index_columns = data.index.names
            self._write(qlist(numpy.array(index_columns), qtype = QSYMBOL_LIST))
            data.reset_index(inplace = True)
            self._buffer.write(struct.pack('=bxi', QGENERAL_LIST, len(index_columns)))
            for column in index_columns:
                self._write_pandas_series(data[column], qtype = data.meta[column] if hasattr(data, 'meta') else None)

            data.set_index(index_columns, inplace = True)

        self._buffer.write(struct.pack('=bxb', QTABLE, QDICTIONARY))
        self._write(qlist(numpy.array(data_columns), qtype = QSYMBOL_LIST))
        self._buffer.write(struct.pack('=bxi', QGENERAL_LIST, len(data_columns)))
        for column in data_columns:
            self._write_pandas_series(data[column], qtype = data.meta[column] if hasattr(data, 'meta') else None)


    @serialize(tuple, list)
    def _write_generic_list(self, data):
        self._buffer.write(struct.pack('=bxi', QGENERAL_LIST, len(data)))
        for element in data:
            # assume nan represents a string null
            self._write(' ' if type(element) in [float, numpy.float32, numpy.float64] and numpy.isnan(element) else element)
