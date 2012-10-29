#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: module for a UNIX socket object class
"""

# Standard modules
import sys
import os
import logging
import socket
import errno
import pwd
import grp
import re

from gettext import gettext as _

# Third party modules

# Own modules
import pb_base.common

from pb_base.object import PbBaseObjectError

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.socket_obj import GenericSocketError
from pb_base.socket_obj import GenericSocket

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.2.0'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

#==============================================================================
class UnixSocketError(GenericSocketError):
    """
    Base error class for all special exceptions raised in this module.
    """

#==============================================================================
class NoSocketFileError(UnixSocketError):
    """
    Error class indicating, that the Unix socket file was not found
    on connecting.
    """

    def __init__(self, filename):
        msg = _("The Unix socket file '%s' was not found.") % (filename)
        super(NoSocketFileError, self).__init__(msg)

#==============================================================================
class UnixSocket(GenericSocket):
    """Class for capsulation a UNIX socket."""

    #--------------------------------------------------------------------------
    def __init__(self,
            filename,
            mode = 040660,
            owner = None,
            group = None,
            timeout = 5,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            ):
        """
        Initialisation of the UnixSocket object.

        @raise UnixSocketError: on a uncoverable error.

        @param filename: the filename of the socket, that should be used
        @type filename: str
        @param mode: The creation mode of the scstadm communication socket.
        @type mode: int
        @param owner: The owning user of the scstadm communication socket
        @type owner: str
        @param group: The owning group of the scstadm communication socket
        @type group: str
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

        super(UnixSocket, self).__init__(
                timeout = timeout,
                appname = appname,
                base_dir = base_dir,
                verbose = verbose,
                version = version,
                use_stderr = use_stderr,
        )

        self._filename = filename
        """
        @ivar: the filename of the socket, that should be used
        @type: str
        """

        self._mode = mode
        """
        @ivar: The creation mode of the scstadm communication socket.
        @type: int
        """

        self._owner = owner
        """
        @ivar: The owning user of the scstadm communication socket
        @type: str
        """

        self._group = group
        """
        @ivar: The owning group of the scstadm communication socket
        @type: str
        """

        # Create a UDS socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    #------------------------------------------------------------
    @property
    def filename(self):
        """The filename of the socket, that should be used."""
        return self._filename

    #------------------------------------------------------------
    @property
    def mode(self):
        """The creation mode of the scstadm communication socket."""
        return self._mode

    #------------------------------------------------------------
    @property
    def owner(self):
        """The owning user of the scstadm communication socket."""
        return self._owner

    #------------------------------------------------------------
    @property
    def group(self):
        """The owning group of the scstadm communication socket."""
        return self._group

    #--------------------------------------------------------------------------
    def __del__(self):
        """Destructor, closes current socket, if necessary."""

        if self.sock and self.bounded and os.path.exists(self.filename):
            if self.verbose > 1:
                log.debug(_("Removing socket '%s' ..."), self.filename)
            os.remove(self.filename)

    #--------------------------------------------------------------------------
    def connect(self):
        """Connecting to the saved socket as a client."""

        if self.verbose > 1:
            log.debug(_("Connecting to Unix Domain Socket '%s' ..."),
                    self.filename)

        try:
            self.sock.connect(self.filename)
        except socket.error, e:
            if e.errno == errno.ENOENT:
                raise NoSocketFileError(self.filename)
            msg = _("Error connecting to Unix Socket '%(sock)s': %(err)s") % {
                    'sock': self.filename, 'err': str(e)}
            raise UnixSocketError(msg)

        self._connected = True

    #--------------------------------------------------------------------------
    def bind(self):
        """Create the socket and listen on it."""

        if self.verbose > 1:
            log.debug(_("Creating and binding to Unix Domain Socket '%s' ..."),
                    self.filename)

        self.sock.bind(self.filename)

        if not os.path.exists(self.filename):
            raise NoSocketFileError(self.filename)

        self._bounded = True

        # Setting mode of socket
        sock_stat = os.stat(self.filename)

        if self.mode is not None:
            if self.verbose > 2:
                log.debug(_("Setting permissions of '%(sock)s' to 0%(perm)o.") % {
                        'sock': self.filename, 'perm': self.mode})
            os.chmod(self.filename, self.mode)

        # Setting owner and group of socket
        uid = -1
        if self.owner is not None:
            if re.search(r'^\d+$', self.owner):
                uid = int(self.owner)
            else:
                try:
                    uid = pwd.getpwnam(self.owner).pw_uid
                except KeyError, e:
                    msg = _("Invalid owner name '%s' for socket creation " +
                            "given.") % (self.owner)
                    raise UnixSocketError(msg)

        gid = -1
        if self.group is not None:
            if re.search(r'^\d+$', self.group):
                gid = int(self.group)
            else:
                try:
                    gid = grp.getgrnam(self.group).gr_gid
                except KeyError, e:
                    msg = _("Invalid group name '%s' for socket creation " +
                            "given.") % (self.group)
                    raise UnixSocketError(msg)

        uid_changed = False
        if uid >= 0:
            if sock_stat.st_uid == uid:
                uid = -1
            else:
                uid_changed = True

        gid_changed = False
        if gid >= 0:
            if sock_stat.st_gid == gid:
                gid = -1
            else:
                gid_changed = True

        if uid_changed or gid_changed:
            if os.geteuid():
                log.warn(_("Only root may change ownership of a socket."))
            else:
                if self.verbose > 2:
                    log.debug(_("Setting ownership of '%(sock)s' to " +
                            "%(uid)d:%(gid)d ...") % {'sock': self.filename,
                            'uid': uid, 'gid': gid})
                os.chown(self.filename, uid, gid)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
