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

from qpython.qtype import *  # @UnusedWildImport



def test_is_null():
    assert is_null(qnull(QSYMBOL), QSYMBOL)
    assert is_null(numpy.string_(''), QSYMBOL)
    assert is_null('', QSYMBOL)
    assert not is_null(' ', QSYMBOL)
    assert not is_null(numpy.string_(' '), QSYMBOL)
    
    assert is_null(qnull(QSTRING), QSTRING)
    assert is_null(' ', QSTRING)
    assert not is_null('', QSTRING)
    assert not is_null(numpy.string_(''), QSTRING)
    assert is_null(numpy.string_(' '), QSTRING)
    
    assert is_null(qnull(QBOOL), QBOOL)
    assert is_null(numpy.bool_(False), QBOOL)
    assert not is_null(numpy.bool_(True), QBOOL)     
    
    for t in QNULLMAP.keys():
        assert is_null(qnull(t), t)


test_is_null()