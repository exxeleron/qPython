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

__all__ = ['qconnection', 'qtype', 'qtemporal', 'qcollection']


__version__ = '2.0.0'



try:
    from qpython.fastutils import uncompress
except:
    __is_cython_enabled__ = False
else:
    __is_cython_enabled__ = True


class MetaData(object):
    '''Utility class for enriching data structures with meta data, e.g. qtype hint.'''
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        if not self.__dict__.items():
            return 'metadata()'

        s = ['metadata(']
        for k, v in self.__dict__.items():
            s.append('%s=%s' % (k, repr(v)))
            s.append(', ')
        s[-1] = ')'
        return ''.join(s)

    def __getattr__(self, attr):
        return None

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def as_dict(self):
        return self.__dict__.copy()

    def union_dict(self, **kw):
        return dict(list(self.as_dict().items()) + list(kw.items()))



CONVERSION_OPTIONS = MetaData(raw = False,
                              numpy_temporals = False,
                              pandas = False,
                              single_char_strings = False
                             )
