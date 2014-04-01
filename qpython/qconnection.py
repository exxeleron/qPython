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

import socket
import struct

from qpython.qtype import QException
from qpython.qreader import QReader, QReaderException
from qpython.qwriter import QWriter, QWriterException


class QConnectionException(Exception):
    pass



class QAuthenticationException(QConnectionException):
    pass



class MessageType(object):
    ASYNC = 0
    SYNC = 1
    RESPONSE = 2



class QConnection(object):
    '''
    Connector class for interfacing with the q service. Provides methods for synchronous and asynchronous interaction.
    '''

    def __init__(self, host, port, username = None, password = None, timeout = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self._connection = None
        self._protocol_version = None

        self.timeout = timeout


    '''Retrieves q protocol version estabilished with remote q service.'''
    @property
    def protocol_version(self):
        return self._protocol_version


    '''Initializes connection to q service.'''
    def open(self):
        if not self._connection:
            if not self.host:
                raise QConnectionException('Host cannot be None')

            self._init_socket()
            self._initialize()

            self._writer = QWriter(self._connection, protocol_version = self._protocol_version)
            self._reader = QReader(self._connection.makefile())


    def _init_socket(self):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((self.host, self.port))
        self._connection.settimeout(self.timeout)


    '''Closes connection with q service.'''
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


    '''
    Checks whether connection has been established. Connection is considered inactive when: 
    - it has not been initialized, 
    - it has been closed.
    '''
    def is_connected(self):
        return True if self._connection else False


    def _initialize(self):
        credentials = self.username + ':' + self.password if self.password else ''
        self._connection.send(credentials + '\3\0')
        response = self._connection.recv(1)

        if len(response) != 1:
            self.close()
            self._init_socket()
        
            self._connection.send(credentials + '\0')
            response = self._connection.recv(1)
            if len(response) != 1:
                self.close()
                raise QAuthenticationException('Connection denied.')

        self._protocol_version = min(struct.unpack('B', response)[0], 3)


    def __str__(self):
        return '%s@:%s:%s' % (self.username, self.host, self.port) if self.username else ':%s:%s' % (self.host, self.port)


    '''
    Performs a query against a q service.
    
    Arguments:
    msg_type    -- type of the query to be executed (as defined in MessageType class)
    query       -- query to be executed
    parameters  -- parameters for the query
    '''
    def query(self, msg_type, query, *parameters):
        if not self._connection:
            raise QConnectionException('Connection is not established.')

        if parameters and len(parameters) > 8:
            raise QWriterException('Too many parameters.')

        if not parameters or len(parameters) == 0:
            return self._writer.write(query, msg_type)
        else:
            return self._writer.write([query] + list(parameters), msg_type)


    '''Performs a synchronous query and returns parsed data.'''
    def sync(self, query, *parameters):
        self.query(MessageType.SYNC, query, *parameters)
        response = self.receive(data_only = False)

        if response.type == MessageType.RESPONSE:
            return response.data
        else:
            self._writer.write(QException('nyi: qPython expected response message'), MessageType.ASYNC if response.type == MessageType.ASYNC else MessageType.RESPONSE)
            raise QReaderException('Received message of type: %s where response was expected')


    '''Performs an asynchronous query and returns without retrieving of the response.'''
    def async(self, query, *parameters):
        self.query(MessageType.ASYNC, query, *parameters)


    '''
    Reads and (optionally) parses the response from q service.
    
    Arguments:
    data_only  -- if True returns only data part of the message
                  if False retuns data and message meta-information encapsulated in QMessage 
    raw        -- if True returns raw data chunk instead of parsed data
    '''
    def receive(self, data_only = True, raw = False):
        result = self._reader.read(raw)
        return result.data if data_only else result


    def __call__(self, *parameters):
        return self.sync(parameters[0], *parameters[1:])
