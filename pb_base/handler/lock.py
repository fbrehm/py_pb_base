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

from numbers import Number

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

# Module variables
default_lockretry_delay_start = 0.1
default_lockretry_delay_increase = 0.2
default_lockretry_max_delay = 10
default_locking_use_pid = True
default_max_lockfile_age = 300

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
class PbLockHandler(PbBaseHandler):
    """
    Handler class with additional properties and methods to create,
    check and remove lock files.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            lockdir = None,
            lockretry_delay_start = default_lockretry_delay_start,
            lockretry_delay_increase = default_lockretry_delay_increase,
            lockretry_max_delay = default_lockretry_max_delay,
            max_lockfile_age = default_max_lockfile_age,
            locking_use_pid = default_locking_use_pid,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            simulate = False,
            sudo = False,
            quiet = False,
            *targs,
            **kwargs
            ):
        """
        Initialisation of the locking handler object.

        @raise LockdirNotExistsError: if the lockdir (or base_dir) doesn't exists
        @raise LockHandlerError: on a uncoverable error.

        @param lockdir: a special directory for searching and creating the
                        lockfiles, if not given, self.base_dir will used
        @type lockdir: str
        @param lockretry_delay_start: the first delay in seconds after an
                                      unsuccessful lockfile creation
        @type lockretry_delay_start: Number
        @param lockretry_delay_increase: seconds to increase the delay in every
                                         wait cycle
        @type lockretry_delay_increase: Number
        @param lockretry_max_delay: the total maximum delay in seconds for
                                    trying to create a lockfile
        @type lockretry_max_delay: Number
        @param max_lockfile_age: the maximum age of the lockfile (in seconds),
                                 for the existing lockfile is valid (if
                                 locking_use_pid is False).
        @type max_lockfile_age: Number
        @param locking_use_pid: write the PID of creating process into the
                                fresh created lockfile, if False, the lockfile
                                will be leaved empty, the PID in the lockfile
                                can be used to check the validity of the
                                lockfile
        @type locking_use_pid: bool
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
        @param simulate: don't execute actions, only display them
        @type simulate: bool
        @param sudo: should the command executed by sudo by default
        @type sudo: bool
        @param quiet: don't display ouput of action after calling
        @type quiet: bool

        @return: None

        """

        super(PbLockHandler, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
                simulate = simulate,
                sudo = sudo,
                quiet = quiet,
        )

        self._lockdir = None
        if lockdir is not None:
            self.lockdir = lockdir

        self._lockretry_delay_start = default_lockretry_delay_start
        self.lockretry_delay_start = lockretry_delay_start

        self._lockretry_delay_increase = default_lockretry_delay_increase
        self.lockretry_delay_increase = lockretry_delay_increase

        self._lockretry_max_delay = default_lockretry_max_delay
        self.lockretry_max_delay = lockretry_max_delay

        self._max_lockfile_age = default_max_lockfile_age
        self.max_lockfile_age = max_lockfile_age

        self._locking_use_pid = default_locking_use_pid
        self.locking_use_pid = locking_use_pid

    #------------------------------------------------------------
    @property
    def lockdir(self):
        """The directory for searching and creating the lockfiles."""
        if self._lockdir:
            return self._lockdir
        return self.base_dir

    @lockdir.setter
    def lockdir(self, value):
        if not value:
            self._lockdir = None
            return

        if os.path.isabs(value):
            self._lockdir = os.path.normpath(value)
        else:
            self._lockdir = os.path.normpath(os.path.join(self.base_dir, value))

    #------------------------------------------------------------
    @property
    def lockretry_delay_start(self):
        """
        The first delay in seconds after an unsuccessful lockfile creation.
        """
        return self._lockretry_delay_start

    @lockretry_delay_start.setter
    def lockretry_delay_start(self, value):
        if not isinstance(value, Number):
            msg = _("Value %r for lockretry_delay_start is not a Number.") % (
                    value)
            raise LockHandlerError(msg)

        if value <= 0:
            msg = _("The value for lockretry_delay_start must be greater " +
                    "than zero (is %r).") % (value)
            raise LockHandlerError(msg)

        self._lockretry_delay_start = value

    #------------------------------------------------------------
    @property
    def lockretry_delay_increase(self):
        """
        The seconds to increase the delay in every wait cycle.
        """
        return self._lockretry_delay_increase

    @lockretry_delay_increase.setter
    def lockretry_delay_increase(self, value):
        if not isinstance(value, Number):
            msg = _("Value %r for lockretry_delay_increase is not a Number.") % (
                    value)
            raise LockHandlerError(msg)

        if value < 0:
            msg = _("The value for lockretry_delay_increase must be greater " +
                    "than or equal to zero (is %r).") % (value)
            raise LockHandlerError(msg)

        self._lockretry_delay_increase = value

    #------------------------------------------------------------
    @property
    def lockretry_max_delay(self):
        """
        The total maximum delay in seconds for trying to create a lockfile.
        """
        return self._lockretry_max_delay

    @lockretry_max_delay.setter
    def lockretry_max_delay(self, value):
        if not isinstance(value, Number):
            msg = _("Value %r for lockretry_max_delay is not a Number.") % (
                    value)
            raise LockHandlerError(msg)

        if value < 0:
            msg = _("The value for lockretry_max_delay must be greater " +
                    "than zero (is %r).") % (value)
            raise LockHandlerError(msg)

        self._lockretry_max_delay = value

    #------------------------------------------------------------
    @property
    def max_lockfile_age(self):
        """
        The maximum age of the lockfile (in seconds), for the existing lockfile
        is valid (if locking_use_pid is False).
        """
        return self._max_lockfile_age

    @max_lockfile_age.setter
    def max_lockfile_age(self, value):
        if not isinstance(value, Number):
            msg = _("Value %r for max_lockfile_age is not a Number.") % (
                    value)
            raise LockHandlerError(msg)

        if value < 0:
            msg = _("The value for max_lockfile_age must be greater " +
                    "than zero (is %r).") % (value)
            raise LockHandlerError(msg)

        self._max_lockfile_age = value

    #------------------------------------------------------------
    @property
    def locking_use_pid(self):
        """
        Write the PID of creating process into the fresh created lockfile.
        """
        return self._locking_use_pid

    @locking_use_pid.setter
    def locking_use_pid(self, value):
        self._locking_use_pid = bool(value)

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbLockHandler, self).as_dict()
        res['lockdir'] = self.lockdir
        res['lockretry_delay_start'] = self.lockretry_delay_start
        res['lockretry_delay_increase'] = self.lockretry_delay_increase
        res['lockretry_max_delay'] = self.lockretry_max_delay
        res['max_lockfile_age'] = self.max_lockfile_age
        res['locking_use_pid'] = self.locking_use_pid

        return res

    #--------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = super(PbLockHandler, self).__repr__()[:-2]

        fields = []
        if self._lockdir:
            fields.append("lockdir=%r" % (self.lockdir))
        fields.append("lockretry_delay_start=%r" % (self.lockretry_delay_start))
        fields.append("lockretry_delay_increase=%r" % (self.lockretry_delay_increase))
        fields.append("lockretry_max_delay=%r" % (self.lockretry_max_delay))
        fields.append("max_lockfile_age=%r" % (self.max_lockfile_age))
        fields.append("locking_use_pid=%r" % (self.locking_use_pid))

        if fields:
            out += ', ' + ", ".join(fields)
        out += ")>"
        return out

#==============================================================================
if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
