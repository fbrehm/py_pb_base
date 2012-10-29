#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: modules for socket object classes
"""

# Standard modules
import sys
import os
import logging

from gettext import gettext as _

from abc import ABCMeta
from abc import abstractmethod

# Third party modules

# Own modules
import pb_base.common

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.1.3'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

#==============================================================================
class GenericSocketError(PbError):
    """
    Base error class for all special exceptions raised in this module.
    """

#==============================================================================
class GenericSocket(PbBaseObject):
    """Class for capsulation a generic socket somehow."""

    __metaclass__ = ABCMeta

    #--------------------------------------------------------------------------
    def __init__(self,
            timeout = 5,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            ):
        """
        Initialisation of the GenericSocket object.

        @raise GenericSocketError: on a uncoverable error.

        @param timeout: timeout in seconds for all opening and IO operations
        @type timeout: int
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

        @return: None
        """

        super(GenericSocket, self).__init__(
                appname = appname,
                base_dir = base_dir,
                verbose = verbose,
                version = version,
                use_stderr = use_stderr,
                initialized = False,
        )

        self._timeout = int(timeout)
        """
        @ivar: timout in seconds for all opening and IO operations
        @type: int
        """

        self._bounded = False
        """
        @ivar: flag indicating, that the socket is bounded for listening
        @type: bool
        """

        self._connected = False
        """
        @ivar: flag indicating, that the application is connected
               to the UNIX socket
        @type: bool
        """

        self._fileno = None
        """
        @ivar: the file number of the socket after binding or connecting
               (used for select())
        @type: int
        """

        self.sock = None
        """
        @ivar: the underlaying socket object
        @type: socket
        """

    #------------------------------------------------------------
    @property
    def timeout(self):
        """timeout in seconds for all opening and IO operations"""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = int(value)

    #------------------------------------------------------------
    @property
    def fileno(self):
        """The file number of the socket after binding or connecting."""
        return self._fileno

    @fileno.setter
    def fileno(self, value):
        self._fileno = int(value)

    #------------------------------------------------------------
    @property
    def connected(self):
        """A flag indicating, that the application is connected to the UNIX socket."""
        return self._connected

    #------------------------------------------------------------
    @property
    def bounded(self):
        """A flag indicating, that the socket is bounded for listening."""
        return self._bounded

    #------------------------------------------------------------
    @property
    def group(self):
        """The owning group of the scstadm communication socket."""
        return self._group

    #--------------------------------------------------------------------------
    @abstractmethod
    def connect(self):
        """Connecting to the saved socket as a client."""

        raise FunctionNotImplementedError('connect', self.__class__.__name__)

    #--------------------------------------------------------------------------
    @abstractmethod
    def bind(self):
        """Create the socket and listen on it."""

        raise FunctionNotImplementedError('bind', self.__class__.__name__)

    #--------------------------------------------------------------------------
    def __del__(self):
        """Destructor, closes current socket, if necessary."""

        if self.sock and (self.connected or self.bounded):
            if self.verbose > 1:
                log.debug(_("Closing socket ..."))
            self.sock.close()

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
