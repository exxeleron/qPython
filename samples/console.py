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

from qpython import qconnection
from qpython.qtype import QException


if __name__ == '__main__':
    with qconnection.QConnection(host = 'localhost', port = 5000) as q:
        print q
        print 'IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected())
    
        while True:
            try:
                x = raw_input('Q)')
            except EOFError:
                print
                break
    
            if x == '\\\\':
                break
    
            try:
                result = q(x)
                print type(result)
                print result
            except QException, msg:
                print 'q error: \'%s' % msg

