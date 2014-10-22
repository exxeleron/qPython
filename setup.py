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

from distutils.core import setup

import numpy
import os

try:
    from Cython.Build import cythonize
except ImportError:
    use_cython = False
else:
    use_cython = True

if use_cython:
    ext_modules = cythonize('qpython/fastutils.pyx')
else:
    ext_modules = []


# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name = 'qPython',
      version = '1.0 RC1',
      description = 'kdb+ interfacing library for Python',
      long_description=read('README.rst'),

      author = 'exxeleron',
      author_email = 'kdbtools@devnet.de',
      url = 'https://github.com/exxeleron/qPython',
      license = 'Apache License Version 2.0',

      ext_modules = ext_modules,
      include_dirs = [numpy.get_include()],

      keywords = ['kdb+'],
      classifiers=[
          'Development Status :: 6 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Financial and Insurance Industry',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Topic :: Database :: Front-Ends',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development',
          ],
      packages = ['qpython', 'samples'],
      package_data = {'': ['LICENSE', 'CHANGELOG.txt', 'README.rst', 'requirements.txt']},
     )
