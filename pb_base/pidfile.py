#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a pidfile object.
          It provides methods to define, check,  create
          and remove a pidfile.
"""

# Standard modules
import sys
import os
import logging
import re

from gettext import gettext as _

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

__version__ = '0.1.0'

log = logging.getLogger(__name__)

#==============================================================================
class PidFileError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    handling a pidfile."""

    pass

#==============================================================================
class PidFile(PbBaseObject):
    """
    Base class for a pidfile object.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
                filename,
                auto_remove = True,
                appname = None,
                verbose = 0,
                version = __version__,
                base_dir = None,
                use_stderr = False,
                initialized = False,
                simulate = False,
                ):
        """
        Initialisation of the pidfile object.

        @raise ValueError: no filename was given
        @raise PidFileError: on some errors.

        @param filename: the filename of the pidfile
        @type filename: str
        @param auto_remove: Remove the self created pidfile on destroying
                            the current object
        @type auto_remove: bool
        @param appname: name of the current running application
        @type appname: str
        @param verbose: verbose level
        @type verbose: int
        @param version: the version string of the current object or application
        @type version: str
        @param base_dir: the base directory of all operations
        @type base_dir: str
        @param use_stderr: a flag indicating, that on handle_error() the output
                           should go to STDERR, even if logging has
                           initialized logging handlers.
        @type use_stderr: bool
        @param initialized: initialisation is complete after __init__()
                            of this object
        @type initialized: bool
        @param simulate: simulation mode
        @type simulate: bool

        @return: None
        """

        super(PidFile, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        if not filename:
            raise ValueError('No filename given on initializing PidFile object.')

        self._filename = os.path.abspath(str(filename))
        """
        @ivar: The filename of the pidfile
        @type: str
        """

        self._auto_remove = bool(auto_remove)
        """
        @ivar: Remove the self created pidfile on destroying the current object
        @type: bool
        """

        self._simulate = bool(simulate)
        """
        @ivar: Simulation mode
        @type: bool
        """

        self._created = False
        """
        @ivar: the pidfile was created by this current object
        @type: bool
        """

    #------------------------------------------------------------
    @property
    def filename(self):
        """The filename of the pidfile."""
        return self._filename

    #------------------------------------------------------------
    @property
    def auto_remove(self):
        """Remove the self created pidfile on destroying the current object."""
        return self._auto_remove

    #------------------------------------------------------------
    @property
    def simulate(self):
        """Simulation mode."""
        return self._simulate

    #------------------------------------------------------------
    @property
    def created(self):
        """The pidfile was created by this current object."""
        return self._created


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
