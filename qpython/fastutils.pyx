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

import numpy
cimport numpy

DTYPE = numpy.int
ctypedef numpy.int_t DTYPE_t
DTYPE8 = numpy.int
ctypedef numpy.uint8_t DTYPE8_t



def uncompress(numpy.ndarray[DTYPE8_t] data, DTYPE_t uncompressed_size):
    cdef DTYPE_t n, r, i, d, s, p, pp, f
    n, r, s, p, pp = 0, 0, 0, 0, 0
    i, d = 1, 1

    cdef numpy.ndarray[DTYPE_t] ptrs = numpy.zeros(256, dtype = DTYPE)
    cdef numpy.ndarray[DTYPE8_t] uncompressed = numpy.zeros(uncompressed_size, dtype = numpy.uint8)
    cdef numpy.ndarray[DTYPE_t] idx = numpy.arange(uncompressed_size, dtype = DTYPE)

    f = 0xff & data[0]

    while s < uncompressed_size:
        pp = p + 1

        if f & i:
            r = ptrs[data[d]]
            n = 2 + data[d + 1]
            uncompressed[idx[s:s + n]] = uncompressed[r:r + n]

            ptrs[uncompressed[p] ^ uncompressed[pp]] = p
            if s == pp:
                ptrs[uncompressed[pp] ^ uncompressed[pp + 1]] = pp

            d += 2
            r += 2
            s = s + n
            p = s

        else:
            uncompressed[s] = data[d]

            if pp == s:
                ptrs[uncompressed[p] ^ uncompressed[pp]] = p
                p = pp

            s += 1
            d += 1

        if i == 128:
            if s < uncompressed_size:
                f = 0xff & data[d]
                d += 1
                i = 1
        else:
            i += i

    return uncompressed
