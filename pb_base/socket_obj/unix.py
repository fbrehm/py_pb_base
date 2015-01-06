#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Frank Brehm, ProfitBricks GmbH, Berlin
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

# Third party modules

# Own modules
import pb_base.common

from pb_base.object import PbBaseObjectError

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.socket_obj import GenericSocketError
from pb_base.socket_obj import GenericSocket

from pb_base.translate import translator, pb_gettext, pb_ngettext

__version__ = '0.3.2'

log = logging.getLogger(__name__)

_ = pb_gettext
__ = pb_ngettext


# =============================================================================
class UnixSocketError(GenericSocketError):
    """
    Base error class for all special exceptions raised in this module.
    """


# =============================================================================
class NoSocketFileError(UnixSocketError):
    """
    Error class indicating, that the Unix socket file was not found
    on connecting.
    """

    def __init__(self, filename):
        msg = _("The Unix socket file %r was not found.") % (filename)
        super(NoSocketFileError, self).__init__(msg)


# =============================================================================
class NoPermissionsToSocketError(UnixSocketError):
    """
    Error class indicating, that the current user doesn't have the right
    permissions to connect to Unix socket.
    """

    def __init__(self, filename):
        msg = _("Invalid permissions to connect to Unix socket %r.") % (filename)
        super(NoPermissionsToSocketError, self).__init__(msg)


# =============================================================================
class UnixSocket(GenericSocket):
    """Class for capsulation a UNIX socket."""

    # -------------------------------------------------------------------------
    def __init__(
        self, filename, mode=0o40660, owner=None, group=None, auto_remove=True,
            timeout=5, request_queue_size=5,
            buffer_size=pb_base.socket_obj.default_buffer_size,
            appname=None, verbose=0, version=__version__, base_dir=None,
            use_stderr=False):
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
        @param auto_remove: Remove the self created socket file on destroying
                            the current object
        @type auto_remove: bool
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

        super(UnixSocket, self).__init__(
            timeout=timeout,
            request_queue_size=request_queue_size,
            buffer_size=buffer_size,
            appname=appname,
            base_dir=base_dir,
            verbose=verbose,
            version=version,
            use_stderr=use_stderr,
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

        self._auto_remove = bool(auto_remove)
        """
        @ivar: Remove the self created socket file on destroying
               the current object
        @type: bool
        """

        self._was_bonded = False

        # Create an UDS socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # -----------------------------------------------------------
    @property
    def filename(self):
        """The filename of the socket, that should be used."""
        return self._filename

    # -----------------------------------------------------------
    @property
    def mode(self):
        """The creation mode of the scstadm communication socket."""
        return self._mode

    # -----------------------------------------------------------
    @property
    def owner(self):
        """The owning user of the scstadm communication socket."""
        return self._owner

    # -----------------------------------------------------------
    @property
    def group(self):
        """The owning group of the scstadm communication socket."""
        return self._group

    # -----------------------------------------------------------
    @property
    def auto_remove(self):
        """
        Remove the self created socket file on destroying
        the current object.
        """
        return self._auto_remove

    @auto_remove.setter
    def auto_remove(self, value):
        self._auto_remove = bool(value)

    # -----------------------------------------------------------
    @property
    def was_bonded(self):
        """Flag, that the socket was bonded by the current object."""
        return self._was_bonded

    # -------------------------------------------------------------------------
    def as_dict(self, short=False):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(UnixSocket, self).as_dict(short=short)
        res['filename'] = self.filename
        res['mode'] = "%04o" % (self.mode)
        res['owner'] = self.owner
        res['group'] = self.group
        res['auto_remove'] = self.auto_remove

        return res

    # -------------------------------------------------------------------------
    def close(self):
        """Closing the current socket."""

        was_bonded = self.bonded

        super(UnixSocket, self).close()

        if self.was_bonded and os.path.exists(self.filename) and self.auto_remove:
            if self.verbose > 1:
                log.debug(_("Removing socket file %r ..."), self.filename)
            os.remove(self.filename)

        self.fileno = None

    # -------------------------------------------------------------------------
    def connect(self):
        """Connecting to the saved socket as a client."""

        if self.verbose > 1:
            log.debug(_(
                "Connecting to Unix Domain Socket '%s' ..."), self.filename)

        if self.connected:
            msg = _("The socket is already connected to '%s' ...") % (self.filename)
            raise UnixSocketError(msg)

        if self.bonded:
            msg = _(
                "The application is already bonded to '%s' ...") % (
                self.filename)
            raise UnixSocketError(msg)

        try:
            self.sock.connect(self.filename)
        except socket.error as e:
            if e.errno == errno.ENOENT:
                raise NoSocketFileError(self.filename)
            if e.errno == errno.EACCES:
                raise NoPermissionsToSocketError(self.filename)
            msg = _("Error connecting to Unix Socket '%(sock)s': %(err)s") % {
                'sock': self.filename, 'err': str(e)}
            raise UnixSocketError(msg)

        self._connected = True
        self.fileno = self.sock.fileno()

    # -------------------------------------------------------------------------
    def bind(self):
        """Create the socket and listen on it."""

        if self.verbose > 1:
            log.debug(_(
                "Creating and binding to Unix Domain Socket '%s' ..."),
                self.filename)

        if self.connected:
            msg = _(
                "The socket is already connected to '%s' ...") % (self.filename)
            raise UnixSocketError(msg)

        if self.bonded:
            msg = _(
                "The application is already bonded to '%s' ...") % (self.filename)
            raise UnixSocketError(msg)

        self._was_bonded = False

        self.sock.bind(self.filename)

        if not os.path.exists(self.filename):
            raise NoSocketFileError(self.filename)

        self._bonded = True
        self._was_bonded = True
        self.fileno = self.sock.fileno()

        # Setting mode of socket
        sock_stat = os.stat(self.filename)

        if self.mode is not None:
            if self.verbose > 2:
                log.debug(_(
                    "Setting permissions of '%(sock)s' to 0%(perm)o.") % {
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
                except KeyError as e:
                    msg = _(
                        "Invalid owner name '%s' for socket creation given.") % (
                        self.owner)
                    raise UnixSocketError(msg)

        gid = -1
        if self.group is not None:
            if re.search(r'^\d+$', self.group):
                gid = int(self.group)
            else:
                try:
                    gid = grp.getgrnam(self.group).gr_gid
                except KeyError as e:
                    msg = _(
                        "Invalid group name '%s' for socket creation given.") % (
                        self.group)
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
                    log.debug(_(
                        "Setting ownership of '%(sock)s' to %(uid)d:%(gid)d ...") % {
                        'sock': self.filename, 'uid': uid, 'gid': gid})
                os.chown(self.filename, uid, gid)

        if self.verbose > 2:
            log.debug(_(
                "Start listening on socket with a queue size of %d."),
                self.request_queue_size)
        self.sock.listen(self.request_queue_size)

# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
