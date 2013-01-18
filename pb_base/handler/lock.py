#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: Module for a extended handler module, which has additional
          methods for locking
"""

# Standard modules
import sys 
import os
import logging

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.object import PbBaseObjectError

from pb_base.handler import PbBaseHandlerError
from pb_base.handler import CommandNotFoundError
from pb_base.handler import PbBaseHandler

from pb_base.translate import translator

__version__ = '0.1.0'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

#==============================================================================
class LockHandlerError(PbBaseHandlerError):
    """
    Base exception class for all exceptions belonging to locking issues
    in this module
    """

    pass

#==============================================================================
class LockdirNotExistsError(LockHandlerError):
    """
    Exception class for the case, that the parent directory of the lockfile
    (lockdir) doesn't exists.
    """

    #--------------------------------------------------------------------------
    def __init__(self, lockdir):
        """
        Constructor.

        @param lockdir: the directory, wich doesn't exists.
        @type lockdir: str

        """

        self.lockdir = lockdir

    #--------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        return _("Locking directory %r doesn't exists.") % (self.lockdir)

#==============================================================================
class LockdirNotWriteableError(LockHandlerError):
    """
    Exception class for the case, that the parent directory of the lockfile
    (lockdir) isn't writeable for the current process.
    """

    #--------------------------------------------------------------------------
    def __init__(self, lockdir):
        """
        Constructor.

        @param lockdir: the directory, wich isn't writeable
        @type lockdir: str

        """

        self.lockdir = lockdir

    #--------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        return _("Locking directory %r isn't writeable.") % (self.lockdir)


#==============================================================================
if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
