#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: The module provides an object class with a dict, which can
          be updated in a recursive way.
          It is originated by Jannis Andrija Schnitzer
'''

# Standard modules
#import sys
#import os
import logging

__author__ = 'jannis@itisme.org (Jannis Andrija Schnitzer)'
__copyright__ = '(c) 2009 Jannis Andrija Schnitzer'
__contact__ = 'jannis@itisme.org'
__version__ = '0.1.0'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

#==============================================================================
class RecursiveDictionary(dict):
    """RecursiveDictionary provides the methods rec_update and iter_rec_update
    that can be used to update member dictionaries rather than overwriting
    them."""

    #--------------------------------------------------------------------------
    def rec_update(self, other, **third):
        """Recursively update the dictionary with the contents of other and
        third like dict.update() does - but don't overwrite sub-dictionaries.
        Example:
        >>> d = RecursiveDictionary({'foo': {'bar': 42}})
        >>> d.rec_update({'foo': {'baz': 36}})
        >>> d
        {'foo': {'baz': 36, 'bar': 42}}
        """

        try:
            iterator = other.iteritems()
        except AttributeError:
            iterator = other

        self.iter_rec_update(iterator)
        self.iter_rec_update(third.iteritems())

    #--------------------------------------------------------------------------
    def iter_rec_update(self, iterator):
        for (key, value) in iterator:
            if key in self and \
                    isinstance(self[key], dict) and isinstance(value, dict):
                self[key] = RecursiveDictionary(self[key])
                self[key].rec_update(value)
            else:
                self[key] = value

    #--------------------------------------------------------------------------
    def __repr__(self):
        return super(self.__class__, self).__repr__()

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
