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

import datetime
import numpy
import random
import threading
import sys
import time

from qpython import qconnection
from qpython.qcollection import qlist
from qpython.qtype import QException, QTIME_LIST, QSYMBOL_LIST, QFLOAT_LIST


class PublisherThread(threading.Thread):

    def __init__(self, q):
        super(PublisherThread, self).__init__()
        self.q = q
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped():
            print('.')
            try:
                # publish data to tick
                # function: .u.upd
                # table: ask
                self.q.sync('.u.upd', numpy.string_('ask'), self.get_ask_data())

                time.sleep(1)
            except QException, e:
                print(e)
            except:
                self.stop()

    def get_ask_data(self):
        c = random.randint(1, 10)

        today = numpy.datetime64(datetime.datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0))

        time = [numpy.timedelta64((numpy.datetime64(datetime.datetime.now()) - today), 'ms') for x in xrange(c)]
        instr = ['instr_%d' % random.randint(1, 100) for x in xrange(c)]
        src = ['qPython' for x in xrange(c)]
        ask = [random.random() * random.randint(1, 100) for x in xrange(c)]

        data = [qlist(time, qtype = QTIME_LIST), qlist(instr, qtype = QSYMBOL_LIST), qlist(src, qtype = QSYMBOL_LIST), qlist(ask, qtype = QFLOAT_LIST)]
        print(data)
        return data


if __name__ == '__main__':
    with qconnection.QConnection(host = 'localhost', port = 17010) as q:
        print(q)
        print('IPC version: %s. Is connected: %s' % (q.protocol_version, q.is_connected()))
        print('Press <ENTER> to close application')

        t = PublisherThread(q)
        t.start()

        sys.stdin.readline()

        t.stop()
        t.join()
