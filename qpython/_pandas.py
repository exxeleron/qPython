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

from collections import OrderedDict

from qpython import MetaData
from qpython.qreader import QReader, READER_CONFIGURATION, QReaderException
from qpython.qcollection import QDictionary, qlist
from qpython.qwriter import QWriter, QWriterException
from qpython.qtype import *



class PandasQReader(QReader):

    parse = Mapper(QReader._reader_map)

    @parse(QDICTIONARY)
    def _read_dictionary(self, qtype = QDICTIONARY, options = READER_CONFIGURATION):
        if options.pandas:
            keys = self._read_object(options = options)
            values = self._read_object(options = options)

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
            return QReader._read_dictionary(self, qtype = qtype, options = options)


    @parse(QTABLE)
    def _read_table(self, qtype = QTABLE, options = READER_CONFIGURATION):
        if options.pandas:
            self._buffer.skip()  # ignore attributes
            self._buffer.skip()  # ignore dict type stamp

            columns = self._read_object(options = options)
            data = self._read_object(options = options)

            odict = OrderedDict()
            meta = MetaData(qtype = QTABLE)
            strcols = []
            for i in xrange(len(columns)):
                if isinstance(data[i], str):
                    # convert character list (represented as string) to numpy representation
                    meta[columns[i]] = QSTRING
                    odict[columns[i]] = numpy.array(list(data[i]), dtype = numpy.str)
                    strcols.append(columns[i])
                elif isinstance(data[i], (list, tuple)):
                    meta[columns[i]] = QGENERAL_LIST
                    tarray = numpy.ndarray(shape = len(data[i]), dtype = numpy.dtype('O'))
                    for j in xrange(len(data[i])):
                        tarray[j] = data[i][j]
                    odict[columns[i]] = tarray
                    strcols.append(columns[i])
                else:
                    meta[columns[i]] = data[i].meta.qtype
                    odict[columns[i]] = data[i]

            df = pandas.DataFrame(odict)
            df.meta = meta
            for column in strcols:
                # q uses the space character as the NULL value for strings
                df[column] = df[column].replace([' ', ''], numpy.nan)
            return df
        else:
            return QReader._read_table(self, qtype = qtype, options = options)


    def _read_list(self, qtype, options):
        if options.pandas:
            options.numpy_temporals = True

        list = QReader._read_list(self, qtype = qtype, options = options)

        if options.pandas:
            if -abs(qtype) not in [QMONTH, QDATE, QDATETIME, QMINUTE, QSECOND, QTIME, QTIMESTAMP, QTIMESPAN, QSYMBOL]:
                null = QNULLMAP[-abs(qtype)][1]
                ps = pandas.Series(data = list).replace(null, numpy.NaN)
            else:
                ps = pandas.Series(data = list)

            ps.meta = MetaData(qtype = qtype)
            return ps
        else:
            return list



class PandasQWriter(QWriter):

    serialize = Mapper(QWriter._writer_map)

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
            qtype = Q_TYPE.get(type(data[0]), QGENERAL_LIST)

        if qtype is None:
            raise QWriterException('Unable to serialize pandas series %s' % data)

        if qtype == QGENERAL_LIST:
            self._write_generic_list(data.as_matrix())
        elif qtype == QCHAR:
            self._write_string(data.as_matrix().astype(numpy.string_).tostring())
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

