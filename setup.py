#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@license: GPL3
@copyright: (c) 2010-2012 by Profitbricks GmbH
@summary: Modules for common used objects, error classes and methods.
"""

from setuptools import setup
import os
import sys
import os.path

# own modules:
cur_dir = os.getcwd()
if sys.argv[0] != '' and sys.argv[0] != '-c':
    cur_dir = os.path.dirname(sys.argv[0])
if os.path.exists(os.path.join(cur_dir, 'pb_base')):
    sys.path.insert(0, os.path.abspath(cur_dir))
del cur_dir

import pb_base

packet_version = pb_base.__version__


setup(
    name = 'pb_base',
    version = packet_version,
    description = 'Modules for common used objects, error classes and methods.',
    author = 'Frank Brehm',
    author_email = 'frank.brehm@profitbricks.com',
    url = 'ssh://git.profitbricks.localdomain/srv/git/python/pb_base.git',
    packages = ['pb_base'],
)

#========================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab

