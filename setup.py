#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@license: LGPL3+
@copyright: © 2010 - 2016 ProfitBricks GmbH, Berlin
@summary: Modules for common used objects, error classes and methods.
"""

import os
import sys
import re
import pprint
import datetime

# Third party modules
import six
from setuptools import setup

# own modules:
cur_dir = os.getcwd()
if sys.argv[0] != '' and sys.argv[0] != '-c':
    cur_dir = os.path.dirname(__file__)

libdir = os.path.join(cur_dir)
bindir = os.path.join(cur_dir, 'bin')
pkg_dir = os.path.join(libdir, 'pb_base')
init_py = os.path.join(pkg_dir, '__init__.py')

if os.path.exists(os.path.join(cur_dir, 'pb_base')):
    sys.path.insert(0, os.path.abspath(cur_dir))

import pb_base

packet_version = pb_base.__version__

packet_name = 'pb_base'
debian_pkg_name = 'profitbricks-python-base'

__author__ = 'Frank Brehm'
__contact__ = 'frank.brehm@profitbricks.com'
__copyright__ = '(C) 2010 - 2016 by ProfitBricks GmbH, Berlin'
__license__ = 'LGPL3+'


# -----------------------------------
def read(fname):
    content = None
    if six.PY3:
        with open(fname, 'r', encoding='utf-8') as fh:
            content = fh.read()
    else:
        with open(fname, 'r') as fh:
            content = fh.read()
    return content


# -----------------------------------
def is_python_file(filename):
    if filename.endswith('.py'):
        return True
    else:
        return False


# -----------------------------------
debian_dir = os.path.join(cur_dir, 'debian')
changelog_file = os.path.join(debian_dir, 'changelog')
readme_file = os.path.join(cur_dir, 'README.txt')


# -----------------------------------
def get_debian_version():
    if not os.path.isfile(changelog_file):
        return None
    changelog = read(changelog_file)
    first_row = changelog.splitlines()[0].strip()
    if not first_row:
        return None
    pattern = r'^' + re.escape(debian_pkg_name) + r'\s+\(([^\)]+)\)'
    match = re.search(pattern, first_row)
    if not match:
        return None
    return match.group(1).strip()

debian_version = get_debian_version()
if debian_version is not None and debian_version != '':
    packet_version = debian_version

# -----------------------------------
local_version_file = os.path.join(pkg_dir, 'local_version.py')
local_version_file_content = '''\
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: %s
@contact: %s
@copyright: © 2010 - %d by %s, Berlin
@summary: Modules for common used objects, error classes and methods.
"""

__author__ = '%s <%s>'
__copyright__ = '(C) 2010 - %d by profitbricks.com'
__contact__ = %r
__version__ = %r
__license__ = %r

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
'''


# -----------------------------------
def write_local_version():

    cur_year = datetime.date.today().year
    content = local_version_file_content % (
        __author__, __contact__, cur_year, __author__, __author__, __contact__,
        cur_year, __contact__, packet_version, __license__)
    # print(content)

    fh = None
    try:
        if six.PY3:
            fh = open(local_version_file, 'wt', encoding='utf-8')
        else:
            fh = open(local_version_file, 'wt')
        fh.write(content)
    finally:
        if fh:
            fh.close

# Write lib/storage_tools/local_version.py
write_local_version()


# -----------------------------------
def pp(obj):
    pprinter = pprint.PrettyPrinter(indent=4)
    return pprinter.pformat(obj)


# -----------------------------------
setup(
    name='pb_base',
    version=packet_version,
    description='Modules for common used objects, error classes and methods.',
    long_description=read('README.txt'),
    author=__author__,
    author_email=__contact__,
    url='ssh://git.profitbricks.localdomain/srv/git/python/pb_base.git',
    license=__license__,
    platforms=['posix'],
    packages=[
        'pb_base',
        'pb_base.handler',
        'pb_base.socket_obj',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    provides=[packet_name],
    scripts=[
        'bin/crc64',
        'bin/term-can-colors',
    ],
    requires=[
        'pb_logging',
        'argparse',
        'configobj',
        'six',
    ]
)

# =======================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
