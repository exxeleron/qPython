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

import numpy



def uncompress(data, uncompressed_size):
    _0 = numpy.intc(0)
    _1 = numpy.intc(1)
    _2 = numpy.intc(2)
    _128 = numpy.intc(128)
    _255 = numpy.intc(255)

    n, r, s, p = _0, _0, _0, _0
    i, d = _1, _1
    f = _255 & data[_0]

    ptrs = numpy.zeros(256, dtype = numpy.intc)
    uncompressed = numpy.zeros(uncompressed_size, dtype = numpy.uint8)
    idx = numpy.arange(uncompressed_size, dtype = numpy.intc)

    while s < uncompressed_size:
        pp = p + _1

        if f & i:
            r = ptrs[data[d]]
            n = _2 + data[d + _1]
            uncompressed[idx[s:s + n]] = uncompressed[r:r + n]

            ptrs[(uncompressed[p]) ^ (uncompressed[pp])] = p
            if s == pp:
                ptrs[(uncompressed[pp]) ^ (uncompressed[pp + _1])] = pp

            d += _2
            r += _2
            s = s + n
            p = s

        else:
            uncompressed[s] = data[d]

            if pp == s:
                ptrs[(uncompressed[p]) ^ (uncompressed[pp])] = p
                p = pp

            s += _1
            d += _1

        if i == _128:
            if s < uncompressed_size:
                f = _255 & data[d]
                d += _1
                i = _1
        else:
            i += i

    return uncompressed
