#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unut tests on base object
'''

import unittest
import os
import sys

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)


#==============================================================================

if __name__ == '__main__':
    unittest.main()

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
