#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: The module for the base object.
          It provides properties and methods used
          by all objects.
'''

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.1.0'
__license__ = 'GPL3'

#==============================================================================
class PbBaseError(Exception):
    '''
    Base error class useable by all descendand objects.
    '''

    pass

#==============================================================================
class PbBaseObject(object):
    """
    Base class for all objects.
    """



#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
