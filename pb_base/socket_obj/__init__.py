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
import re
import select
import time

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
from pb_base.errors import PbIoTimeoutError

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.2.1'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

default_buffer_size = 8192
min_buffer_size = 512
max_buffer_size = (1024 * 1024 * 10)

re_first_line = re.compile(r'^([^\n]*)(\r?\n)')

#==============================================================================
class GenericSocketError(PbError):
    """
    Base error class for all special exceptions raised in this module.
    """

#==============================================================================
class SocketReadTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on reading from socket.
    """

    #--------------------------------------------------------------------------
    def __init__(self, timeout):
        """
        Constructor.

        @param timeout: the timout in seconds leading to the error
        @type timeout: float

        """

        strerror = _("Timeout error on reading from socket")
        super(SocketReadTimeoutError, self).__init__(strerror, timeout)

#==============================================================================
class SocketWriteTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on writing to a socket.
    """

    #--------------------------------------------------------------------------
    def __init__(self, timeout):
        """
        Constructor.

        @param timeout: the timout in seconds leading to the error
        @type timeout: float

        """

        strerror = _("Timeout error on writing to socket")
        super(SocketWriteTimeoutError, self).__init__(strerror, timeout)

#==============================================================================
class GenericSocket(PbBaseObject):
    """Class for capsulation a generic socket somehow."""

    __metaclass__ = ABCMeta

    #--------------------------------------------------------------------------
    def __init__(self,
            timeout = 5,
            request_queue_size = 5,
            buffer_size = default_buffer_size,
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
        @param request_queue_size: the maximum number of queued connections
                                    (between 0 and 5)
        @type request_queue_size: int
        @param buffer_size: The size of the buffer for receiving data from sockets
        @type buffer_size: int
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

        self._request_queue_size = int(request_queue_size)
        """
        @ivar: the maximum number of queued connections (between 0 and 5)
        @type: int
        """
        if self._request_queue_size < 0 or self._request_queue_size > 5:
            raise ValueError(_("Invalid request_queue_size %r, must be " +
                    "between 0 and 5.") % (request_queue_size))

        self._buffer_size = buffer_size
        """
        @ivar: The size of the buffer for receiving data from sockets
        @type: int
        """
        if (self._buffer_size < min_buffer_size or
                self._buffer_size > max_buffer_size):
            raise ValueError(_("Invalid buffer size %(bs)r, must be " +
                    "between %(min)d and %(max)d.") % {'bs': buffer_size,
                    'min': min_buffer_size, 'max': max_buffer_size})

        self._bonded = False
        """
        @ivar: flag indicating, that the socket is bonded for listening
        @type: bool
        """

        self._connected = False
        """
        @ivar: flag indicating, that the application is connected
               to the UNIX socket
        @type: bool
        """

        self._interrupted = False
        """
        @ivar: flag indicating, that the counterpart in communication
               has closed the current socket.
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

        self.connection = None
        """
        @ivar: a socket object after a successful accept()
        @type: socket.socket
        """

        self.client_address = None
        """
        @ivar: the client address after establishing a socket connection
        @type: object
        """

        self._input_buffer = ''
        """
        @ivar: the input buffer for all reading actions
        @type: str
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
    def bonded(self):
        """A flag indicating, that the socket is bonded for listening."""
        return self._bonded

    #------------------------------------------------------------
    @property
    def interrupted(self):
        """
        A flag indicating, that the counterpart in communication
        has closed the current socket.
        """
        return self._interrupted

    @interrupted.setter
    def interrupted(self, value):
        self._interrupted = bool(value)

    #------------------------------------------------------------
    @property
    def request_queue_size(self):
        """The maximum number of queued connections."""
        return self._request_queue_size

    #------------------------------------------------------------
    @property
    def buffer_size(self):
        """The size of the buffer for receiving data from sockets."""
        return self._buffer_size

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

        if self.sock and (self.connected or self.bonded):
            if self.verbose > 1:
                log.debug(_("Closing socket ..."))
            self.sock.close()

    #--------------------------------------------------------------------------
    def reset(self):
        """
        Resetting the socket after interruption of communication.
        """

        if self.verbose > 2:
            log.debug(_("Resetting connection ..."))

        if self.connection:
            self.connection.close()
        self.connection = None
        self.client_address = None
        self.interrupted = False

    #--------------------------------------------------------------------------
    def send(self, message):
        """
        Sends the message over the socket to the communication partner.

        @param message: the message to send
        @type message: str

        """

        if not self.connection or self.interrupted:
            msg = _("Cannot send message to the receipient, because " +
                    "the socket connection is closed.")
            raise GenericSocketError(msg)

        if self.verbose > 2:
            log.debug(_("Sending %r to socket."), message)
        self.connection.send(message)

    #--------------------------------------------------------------------------
    def accept(self):
        """Accept a connection, if the socket is bonded in listening mode."""

        if not self.bonded:
            msg = _("Cannot accept connection, socket is not bonded.")
            raise GenericSocketError(msg)

        connection, client_address = self.sock.accept()
        self.connection = connection
        self.client_address = client_address
        cla = str(client_address)
        if cla:
            cla = _("Got a request from '%s'.") % (cla)
        else:
            cla = _("Got a request from somewhere from system.")
        log.debug(cla)

    #--------------------------------------------------------------------------
    def _read(self):
        """
        Reading data from current socket (from self.connection, if
        there is such one after accept(), or from self.sock) and store the
        data in self._input_buffer.

        I assume, that there are some data on the socket, so this call is
        not blocking. If it isn't so, then the call to this method is
        blocking.

        It reads exact one time from socket. If nothing was read, then the
        counterpart of communication has closed the socket, and
        self.interrupted is set to True.

        """

        if self.verbose > 3:
            log.debug(_("Trying to get data ..."))
        data = self.connection.recv(self.buffer_size)

        if data:
            if self.verbose > 2:
                log.debug(_("Got data: %r.") % (data))
            self._input_buffer += data
            return

        if self.verbose > 2:
            log.debug(_("Got EOF, counterpart has interrupted ..."))
        self.interrupted = True
        return

    #--------------------------------------------------------------------------
    def read_line(self, socket_has_data = False):
        """
        Reads exact one line of data from socket and gives it back.

        This reading action is performed either from self.connection, if
        there is such one after accept(), or from self.sock.

        I assume, that there are some data on the socket, so this call is
        not blocking. If it isn't so, then the call to this method is
        blocking (if has_data was set to False).

        If there was more than one line read at once, the rest is saved
        self._input_buffer.

        @param socket_has_data: assumes, that there are some data on the socket,
                                that can be read. If False, then read_line()
                                checks, with select, whether there are some data
                                on the socket
        @type socket_has_data: bool

        @return: the first line from self._input_buffer including the
                 EOL character
        @rtype: str

        """

        # Checking, whether to read from socket
        if not socket_has_data:
            if self.has_data():
                socket_has_data = True

        # Read in all data, they are even on socket.
        if socket_has_data:
            if not self.connection:
                self.accept()
            while socket_has_data:
                self._read()
                if self.interrupted:
                    socket_has_data = False
                else:
                    socket_has_data = self.has_data()

        if self.interrupted:
            self.reset()

        if self.verbose > 3:
            log.debug(_("Performing input buffer ..."))

        if self._input_buffer:
            if self.verbose > 3:
                log.debug(_("Current input buffer: %r"), self._input_buffer)
            match = re_first_line.search(self._input_buffer)
            if match:
                line = match.group(1) + match.group(2)
                self._input_buffer = re_first_line.sub('', self._input_buffer)
                if self.verbose > 3:
                    log.debug(_("Got a line: %r"), line)
                    log.debug(_("Current input buffer after read_line(): %r"),
                            self._input_buffer)
                return line
            else:
                return ''

        return ''

    #--------------------------------------------------------------------------
    def has_data(self, polling_interval = 0.05):
        """
        Looks, whether the current socket has data in his input buffer, that
        can be read in.

        @return: there are some data to read
        @rtype: bool

        """

        result = False

        try:
            rlist, wlist, elist = select.select(
                    [self.fileno],
                    [],
                    [],
                    polling_interval
            )
            if self.fileno in rlist:
                result = True
        except select.error, e:
            if e[0] == 4:
                pass

        return result

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
