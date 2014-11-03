#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Frank Brehm, ProfitBricks GmbH, Berlin
@license: GPL3
@summary: module for a TCP socket object class
"""

# Standard modules
import sys
import os
import logging
import socket
import errno
import re
import socket

# Third party modules

# Own modules
import pb_base.common

from pb_base.object import PbBaseObjectError

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.socket_obj import GenericSocketError
from pb_base.socket_obj import GenericSocket

from pb_base.translate import translator

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010 - 2014 by Frank Brehm, ProfitBricks GmbH, Berlin'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.1.0'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext
if sys.version_info[0] > 2:
    _ = translator.gettext
    __ = translator.ngettext

PORT_ERR_MSG = _("The TCP port number must be a positive integer value, not %d.")


# =============================================================================
class TcpSocketError(GenericSocketError):
    """
    Base error class for all special exceptions raised in this module.
    """
    pass


# =============================================================================
class CouldNotOpenSocketError(TcpSocketError):
    """Special exception class for the case, the socket could not opened."""
    pass


# =============================================================================
class TcpSocket(GenericSocket):
    """Class for capsulation a TCP socket."""

    # -------------------------------------------------------------------------
    def __init__(
        self, address, port, addr_family=None, address_info_flags=0, timeout=5,
            request_queue_size=5,
            buffer_size=pb_base.socket_obj.default_buffer_size,
            appname=None, verbose=0, version=__version__, base_dir=None,
            use_stderr=False):
        """
        Initialisation of the TcpSocket object.

        @raise TcpSocketError: on a uncoverable error.

        @param address: the hostname or IP address, where to connect to
                        or on which listening to.
                        If it can be converted to a IPy.IP object, an
                        IP address is assumed.
                        If None is given, then the socket will listen on
                        all local IP addresses - not usable for client
                        sockets.
                        Else a hostname is assumed.
        @type address: str or IPy.IP or None
        @param port: the TCP port number, where to connect to or on which
                     should be listened.
        @type port: int
        @param addr_family: the IP address family, may be socket.AF_INET
                            or socket.AF_INET6 or None (for both).
                            If None, in client mode will tried to connect
                            first to an IPv6 address, then IPv4 address.
                            If None in listening mode it will listen on both
                            IPv6 and IPv4.
        @type addr_family: int or None
        @param address_info_flags: additional address information flags, used
                                   by socket.getaddrinfo(),
                                   see "man getaddrinfo" for more information
        @type address_info_flags: int
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

        super(TcpSocket, self).__init__(
            timeout=timeout,
            request_queue_size=request_queue_size,
            buffer_size=buffer_size,
            appname=appname,
            base_dir=base_dir,
            verbose=verbose,
            version=version,
            use_stderr=use_stderr,
        )

        self._address = address
        """
        @ivar: The hostname or IP address, where to connect to or on which listening to.
        @type: str or IPy.IP
        """

        self._address_info_flags = int(address_info_flags)
        """
        @ivar: additional address information flags, used by socket.getaddrinfo()
               see "man getaddrinfo", which are possible
        @type: int
        """

        self._resolved_address = None
        """
        @ivar: The resolved IP address, where to connect to or on which listening to.
               If self.address is '*', the self.resolved_address stays to None.
        @type: IPy.IP or None
        """

        self._port = int(port)
        """
        @ivar: The TCP port number, where to connect to or on which should be listened.
        @type: int
        """
        if self.port < 1:
            raise TcpSocketError(PORT_ERR_MSG % (self.port))

        self._addr_family = addr_family
        """
        @ivar: The IP address family.
        @type: int or None
        """
        if addr_family is not None:
            if addr_family not in (socket.AF_INET, socket.AF_INET6):
                msg = (_(
                    "The IP address family must be one of %(a1)r, %(a2)r or %(a3)r.") % {
                    'a1': 'socket.AF_INET', 'a2': 'socket.AF_INET6', 'a3': None})
                raise TcpSocketError(msg)

        self._used_addr_family = None
        self._used_socket_type = None
        self._used_protocol = None
        self._used_canon_name = None
        self._used_socket_addr = None
        self._own_address = None

        self.initialized = True

    # -----------------------------------------------------------
    @property
    def address(self):
        """The hostname or IP address, where to connect to or on which listening to."""
        return self._address

    # -----------------------------------------------------------
    @property
    def address_info_flags(self):
        """Additional address information flags, used by socket.getaddrinfo()."""
        return self._address_info_flags

    # -----------------------------------------------------------
    @property
    def resolved_address(self):
        """The resolved IP address, where to connect to or on which listening to."""
        return self._resolved_address

    # -----------------------------------------------------------
    @property
    def port(self):
        """The TCP port number, where to connect to or on which should be listened."""
        return self._port

    @port.setter
    def port(self, value):
        v = int(value)
        if v < 1:
            raise TcpSocketError(PORT_ERR_MSG % (v))

    # -----------------------------------------------------------
    @property
    def addr_family(self):
        """The IP address family."""
        return self._addr_family

    # -----------------------------------------------------------
    @property
    def used_addr_family(self):
        """The used IP address family after connecting or binding."""
        return self._used_addr_family

    # -----------------------------------------------------------
    @property
    def used_socket_type(self):
        """The used socket type after connecting or binding."""
        return self._used_socket_type

    # -----------------------------------------------------------
    @property
    def used_protocol(self):
        """The used IP protocol after connecting or binding."""
        return self._used_protocol

    # -----------------------------------------------------------
    @property
    def used_canon_name(self):
        """A string representing the canonical name of the host,
            if socket.AI_CANONNAME is part of self.address_info_flags;
            else used_canon_name will be empty."""
        return self._used_canon_name

    # -----------------------------------------------------------
    @property
    def used_socket_addr(self):
        """A tuple describing a socket address, whose format depends
            on used_addr_family (a (address, port) 2-tuple for AF_INET,
            a (address, port, flow info, scope id) 4-tuple for AF_INET6),
            and is meant to be passed to the socket.connect() method.."""
        return self._used_socket_addr

    # -----------------------------------------------------------
    @property
    def own_address(self):
        """The socket’s own address."""
        return self._own_address

    # -------------------------------------------------------------------------
    def as_dict(self, short=False):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(TcpSocket, self).as_dict(short=short)
        res['address'] = self.address
        res['resolved_address'] = self.resolved_address
        res['address_info_flags'] = self.address_info_flags
        res['port'] = self.port
        res['addr_family'] = self.addr_family
        res['used_addr_family'] = self.used_addr_family
        res['used_socket_type'] = self.used_socket_type
        res['used_protocol'] = self.used_protocol
        res['used_canon_name'] = self.used_canon_name
        res['used_socket_addr'] = self.used_socket_addr
        res['own_address'] = self.own_address

        return res

    # -------------------------------------------------------------------------
    def close(self):
        """Closing the current socket."""

        super(TcpSocket, self).close()
        self._used_addr_family = None
        self._used_socket_type = None
        self._used_protocol = None
        self._used_canon_name = None
        self._used_socket_addr = None
        self._own_address = None
        self.fileno = None

    # -------------------------------------------------------------------------
    def connect(self):
        """Connecting to the TCP socket as a client."""

        if self.address is None:
            msg = _("Cannot connect to an undefined IP address.")
            raise TcpSocketError(msg)

        if self.verbose > 2:
            log.debug(_(
                "Connecting to TCP address %(addr)r, port %(port)d ...") % {
                'addr': self.address, 'port': self.port})

        if self.connected:
            msg = _(
                "The socket is already connected to %(addr)r, port %(port)d ...") % {
                'addr': self.address, 'port': self.port}
            raise TcpSocketError(msg)

        if self.bonded:
            msg = _(
                "The application is allready bonded to %(addr)r, port %(port)d ...") % {
                'addr': self.address, 'port': self.port}
            raise TcpSocketError(msg)

        ai_flags = self.address_info_flags & ~socket.AI_PASSIVE
        self.sock = None
        self._used_addr_family = None
        self._used_socket_type = None
        self._used_protocol = None
        self._used_canon_name = None
        self._used_socket_addr = None
        self._resolved_address = None
        self._own_address = None
        family = None
        socktype = None
        proto = None
        canonname = None
        sockaddr = None

        # Probing for the first matching socket address and connecting
        for ai_result in socket.getaddrinfo(
                self.address, self.port, socket.AF_UNSPEC,
                socket.SOCK_STREAM, 0, ai_flags):

            family, socktype, proto, canonname, sockaddr = ai_result
            if self.verbose > 2:
                msg = (_("TCP %s results:") % ('getaddrinfo()')) + ' ' + str(ai_result)
                log.debug(msg)

            if self.addr_family is not None:
                if self.addr_family != family:
                    continue

            try:
                self.sock = socket.socket(family, socktype, proto)
            except socket.error as msg:
                self.sock = None
                continue

            try:
                self.sock.connect(sockaddr)
            except socket.error as msg:
                self.sock.close()
                self.sock = None
                continue

            break

        # Could not open socket
        if self.sock is None:
            msg = _(
                "Could not open socket to %(addr)r, port %(port)d.") % {
                'addr': self.address, 'port': self.port}
            raise CouldNotOpenSocketError(msg)

        self._connected = True
        self.fileno = self.sock.fileno()
        self._used_addr_family = family
        self._used_socket_type = socktype
        self._used_protocol = proto
        self._used_canon_name = canonname
        self._used_socket_addr = sockaddr
        self._resolved_address = sockaddr[0]
        self._own_address = self.sock.getsockname()

    # -------------------------------------------------------------------------
    def bind(self):
        """Create a TCP socket and listen on it."""

        msg_args = {'addr': '*', 'port': self.port}
        if self.self.address:
            msg_args['addr'] = self.self.address

        if self.verbose > 1:
            msg = _("Creating a listening TCP socket on address %(addr)r, port %(port)d ...")
            log.debug(msg % msg_args)

        if self.connected:
            msg = _("The socket is already connected to address %(addr)r, port %(port)d...")
            raise TcpSocketError(msg % msg_args)

        if self.bonded:
            msg = _("The application is already bonded to address %(addr)r, port %(port)d...")
            raise TcpSocketError(msg % msg_args)

        ai_flags = self.address_info_flags | socket.AI_PASSIVE
        self.sock = None
        self._used_addr_family = None
        self._used_socket_type = None
        self._used_protocol = None
        self._used_canon_name = None
        self._used_socket_addr = None
        self._resolved_address = None
        self._own_address = None
        family = None
        socktype = None
        proto = None
        canonname = None
        sockaddr = None

        # Probing for the first matching socket address and binding
        for ai_result in socket.getaddrinfo(
                self.address, self.port, socket.AF_UNSPEC,
                socket.SOCK_STREAM, 0, ai_flags):

            family, socktype, proto, canonname, sockaddr = ai_result
            if self.verbose > 2:
                msg = (_("TCP %s results:") % ('getaddrinfo()')) + ' ' + str(ai_result)
                log.debug(msg)

            if self.addr_family is not None:
                if self.addr_family != family:
                    continue

            try:
                self.sock = socket.socket(family, socktype, proto)
            except socket.error as msg:
                self.sock = None
                continue

            try:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind(sockaddr)
                self.sock.listen(self.request_queue_size)
            except socket.error as msg:
                self.sock.close()
                self.sock = None
                continue

            # precedence for IPv6
            if family == socket.AF_INET6:
                break

        self._bonded = True
        self.fileno = self.sock.fileno()

        # Could not open socket
        if self.sock is None:
            msg = _("Could not open listening TCP socket on %(addr)r, port %(port)d.")
            raise CouldNotOpenSocketError(msg % msg_args)

        self._connected = True
        self.fileno = self.sock.fileno()
        self._used_addr_family = family
        self._used_socket_type = socktype
        self._used_protocol = proto
        self._used_canon_name = canonname
        self._used_socket_addr = sockaddr
        self._resolved_address = sockaddr[0]
        self._own_address = self.sock.getsockname()

        log.debug(_("Binding TCP socket to server address: %s"), self.own_address)

# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
