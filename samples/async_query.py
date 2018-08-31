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

import random
import threading
import time

from qpython import qconnection
from qpython.qtype import QException
from qpython.qconnection import MessageType
from qpython.qcollection import QDictionary


class ListenerThread(threading.Thread):
    
    def __init__(self, q):
        super(ListenerThread, self).__init__()
        self.q = q
        self._stopper = threading.Event()

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        while not self.stopped():
            print('.')
            try:
                message = self.q.receive(data_only = False, raw = False) # retrieve entire message
                
                if message.type != MessageType.ASYNC:
                    print('Unexpected message, expected message of type: ASYNC')
                    
                print('type: %s, message type: %s, data size: %s, is_compressed: %s ' % (type(message), message.type, message.size, message.is_compressed))
                print(message.data)
                
                if isinstance(message.data, QDictionary):
                    # stop after 10th query
                    if message.data[b'queryid'] == 9:
                        self.stop()
                    
            except QException as e:
                print(e)


if __name__ == '__main__':
    # create connection object
    q = qconnection.QConnection(host = 'localhost', port = 5000)
    # initialize connection
    q.open()

    print(q)
    print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))

    try:
        # definition of asynchronous multiply function
        # queryid - unique identifier of function call - used to identify
        # the result
        # a, b - parameters to the query
        q.sync('asynchMult:{[queryid;a;b] res:a*b; (neg .z.w)(`queryid`result!(queryid;res)) }');

        t = ListenerThread(q)
        t.start()
         
        for x in range(10):
            a = random.randint(1, 100)
            b = random.randint(1, 100)
            print('Asynchronous call with queryid=%s with arguments: %s, %s' % (x, a, b))
            q.send('asynchMult', x, a, b);
        
        time.sleep(1)
    finally:
        q.close()
