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

import qpython
from qpython import qconnection
from qpython.qtype import QException

try:
    input = raw_input
except NameError:
    pass


if __name__ == '__main__':
    print('qPython %s Cython extensions enabled: %s' % (qpython.__version__, qpython.__is_cython_enabled__))
    with qconnection.QConnection(host = 'localhost', port = 5000) as q:
        print(q)
        print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))

        while True:
            try:
                x = input('Q)')
            except EOFError:
                print('')
                break

            if x == '\\\\':
                break

            try:
                result = q(x)
                print(type(result))
                print(result)
            except QException as msg:
                print('q error: \'%s' % msg)

