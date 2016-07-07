#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.abspath('lib'))
from itsm_ansible import __version__, __author__

try:
    from setuptools import setup, find_packages
except ImportError:
    print("itsm_ansible now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

print(find_packages('lib'))

setup(name='itsm_ansible',
      version=__version__,
      description='itsm_ansible use for itsm to deploy app',
      author=__author__,
      author_email='ganjl@ffcs.cn',
      url='http://www.ffcs.cn/',
      # license='GPLv3',
      # Ansible will also make use of a system copy of python-six if installed but use a
      # Bundled copy if it's not.
      install_requires=['ansible == 2.0.1.0'],
      package_dir={'': 'lib'},
      packages=find_packages('lib'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      scripts=[
          'bin/itsm-ansible',
      ],
      data_files=[],
      )
