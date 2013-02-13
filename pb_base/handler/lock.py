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
import time
import errno
import traceback
import datetime

from numbers import Number

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

from pb_base.handler import PbBaseHandlerError
from pb_base.handler import CommandNotFoundError
from pb_base.handler import PbBaseHandler

from pb_base.translate import translator

__version__ = '0.2.1'

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
class LockObjectError(LockHandlerError):
    """
    Special exception class for exceptions raising inside methods of
    the PbLock.
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

        return _("Locking directory %r doesn't exists or is not a directory.") % (
                self.lockdir)

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
class PbLock(PbBaseObject):
    """
    Capsulation class as a result of a successful lock action. It contains all
    important informations about the lock.

    It can be used for holding these informations and, if desired, to remove
    the lock automatically, if the current instance of PbLock is removed.

    """

    #--------------------------------------------------------------------------
    def __init__(self,
            lockfile,
            ctime = None,
            mtime = None,
            fcontent = None,
            simulate = False,
            autoremove = False,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
    ):
        """
        Initialisation of the PbLock object.

        @raise LockObjectError: on a uncoverable error.

        @param lockfile: the file, which represents the lock, must exists
        @type lockfile: str
        @param ctime: the creation time of the lockfile
        @type ctime: datetime
        @param mtime: the modification time of the lockfile
        @type mtime: datetime
        @param fcontent: the content of the lockfile
        @type fcontent: str
        @param simulate: don't execute actions, only display them
        @type simulate: bool
        @param autoremove: removing the lockfile on deleting the current object
        @type autoremove: bool
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

        super(PbLock, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        if not lockfile:
            msg = _("No lockfile given on init of a PbLock object.")
            raise LockObjectError(msg)

        if not os.path.exists(lockfile):
            msg = _("Lockfile %r doesn't exists.") % (lockfile)

            raise LockObjectError(msg)

        if not os.path.isfile(lockfile):
            msg = _("Lockfile %r is not a regular file.") % (lockfile)

            raise LockObjectError(msg)

        self._lockfile = os.path.realpath(lockfile)

        self._fcontent = None
        if fcontent is not None:
            self._fcontent = str(fcontent)
        self._simulate = bool(simulate)
        self._autoremove = bool(autoremove)

        self._ctime = ctime
        self._mtime = mtime

        # Detecting self._ctime and self._mtime from filestat of the lockfile
        if not self._ctime or not self._mtime:
            fstat = os.stat(lockfile)
            if not self._ctime:
                self._ctime = datetime.datetime.utcfromtimestamp(fstat.st_ctime)
            if not self._mtime:
                self._mtime = datetime.datetime.utcfromtimestamp(fstat.st_mtime)

        self.initialized = True

    #------------------------------------------------------------
    @property
    def lockfile(self):
        """The file, which represents the lock."""
        return self._lockfile

    #------------------------------------------------------------
    @property
    def ctime(self):
        """The creation time of the lockfile."""
        return self._ctime

    #------------------------------------------------------------
    @property
    def mtime(self):
        """The last modification time of the lockfile."""
        return self._mtime

    #------------------------------------------------------------
    @property
    def fcontent(self):
        """The content of the lockfile."""
        return self._fcontent

    #------------------------------------------------------------
    @property
    def simulate(self):
        """Don't execute actions, only display them."""
        return self._simulate

    @simulate.setter
    def simulate(self, value):
        self._simulate = bool(value)

    #------------------------------------------------------------
    @property
    def autoremove(self):
        """Removing the lockfile on deleting the current object."""
        return self._autoremove

    @autoremove.setter
    def autoremove(self, value):
        self._autoremove = bool(value)

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbLock, self).as_dict(short = short)
        res['lockfile'] = self.lockfile
        res['ctime'] = self.ctime
        res['mtime'] = self.mtime
        res['fcontent'] = self.fcontent
        res['simulate'] = self.simulate
        res['autoremove'] = self.autoremove

        return res

    #--------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = super(PbLock, self).__repr__()[:-2]

        fields = []
        fields.append("lockfile={!r}".format(self.lockfile))
        if self.fcontent:
            fields.append("fcontent={!r}".format(self.fcontent))
        fields.append("ctime={!r}".format(self.ctime))
        fields.append("mtime={!r}".format(self.mtime))
        fields.append("fcontent={!r}".format(self.fcontent))
        fields.append("simulate={!r}".format(self.simulate))
        fields.append("autoremove={!r}".format(self.autoremove))

        if fields:
            out += ', ' + ", ".join(fields)
        out += ")>"
        return out

    #--------------------------------------------------------------------------
    def __del__(self):
        """Destructor.

        Removes the lockfile, if self.autoremove is True

        """

        if not getattr(self, '_initialized', False):
            return

        if self.autoremove and self.exists:

            msg = _("Automatic removing of %r ...") % (self.lockfile)
            log.info(msg)

            if not self.simulate:
                os.remove(self.lockfile)

    #--------------------------------------------------------------------------
    def exists(self):
        """Returns, whether the lockfile exists or not."""

        if self.simulate:
            return True

        return os.path.exists(self.lockfile)

    #--------------------------------------------------------------------------
    def refresh(self):
        """
        Refreshes the atime and mtime of the lockfile to the current time.
        """

        msg = _("Refreshing atime and mtime of %r to the current timestamp.") % (
                self.lockfile)
        log.debug(msg)

        if not self.simulate:
            os.utime(self.lockfile, None)

        self._mtime = datetime.datetime.utcnow()

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
            msg = _("Value %(val)r for %(what)s is not a Number.") % {
                    'val': value, 'what': 'lockretry_delay_start'}
            raise LockHandlerError(msg)

        if value <= 0:
            msg = _("The value for %(what)s must be greater " +
                    "than zero (is %(val)r).") % {
                    'val': value, 'what': 'lockretry_delay_start'}
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
            msg = _("Value %(val)r for %(what)s is not a Number.") % {
                    'val': value, 'what': 'lockretry_delay_increase'}
            raise LockHandlerError(msg)

        if value < 0:
            msg = _("The value for %(what)s must be greater than or " +
                    "equal to zero (is %(val)r).") % {
                    'val': value, 'what': 'lockretry_delay_increase'}
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
            msg = _("Value %(val)r for %(what)s is not a Number.") % {
                    'val': value, 'what': 'lockretry_max_delay'}
            raise LockHandlerError(msg)

        if value <= 0:
            msg = _("The value for %(what)s must be greater " +
                    "than zero (is %(val)r).") % {
                    'val': value, 'what': 'lockretry_max_delay'}
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
            msg = _("Value %(val)r for %(what)s is not a Number.") % {
                    'val': value, 'what': 'max_lockfile_age'}
            raise LockHandlerError(msg)

        if value <= 0:
            msg = _("The value for %(what)s must be greater " +
                    "than zero (is %(val)r).") % {
                    'val': value, 'what': 'max_lockfile_age'}
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
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbLockHandler, self).as_dict(short = short)
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

    #--------------------------------------------------------------------------
    def create_lockfile(self, lockfile,
            delay_start = None, delay_increase = None, max_delay = None,
            use_pid = None, max_age = None, pid = None):
        """
        Tries to create the given lockfile exclusive.

        If the lockfile exists and is valid, it waits a total maximum
        of max_delay seconds an increasing amount of seconds to get exclusive
        access to the lockfile.

        @param lockfile: the lockfile to use as a semaphore, if not given
                         as an absolute path, it will be supposed to be
                         relative to self.lockdir.
        @type lockfile: str
        @param delay_start: the first delay in seconds after an unsuccessful
                            lockfile creation, if not given,
                            self.lockretry_delay_start will used.
        @type delay_start: Number (or None)
        @param delay_increase: seconds to increase the delay in every wait
                               cycle, if not given, self.lockretry_delay_increase
                               will used.
        @type delay_increase: Number
        @param max_delay: the total maximum delay in seconds for trying
                          to create a lockfile, if not given,
                          self.lockretry_max_delay will used.
        @type max_delay: Number
        @param use_pid: write the PID of creating process into the fresh
                        created lockfile, if not given, self.locking_use_pid
                        will used.
        @type use_pid: bool
        @param max_age: the maximum age of the lockfile (in seconds), for the
                        existing lockfile is valid (if locking_use_pid is False).
        @type max_age: Number
        @param pid: the pid to write into the lockfile, if use_pid is set
                    to True, if not given, the PID of the current process is used.
        @type pid: int

        @return: a lock object on success, else None
        @rtype: PbLock or None

        """

        if delay_start is None:
            delay_start = self.lockretry_delay_start
        else:
            if not isinstance(delay_start, Number):
                msg = _("Value %(val)r for %(what)s is not a Number.") % {
                        'val': delay_start, 'what': 'delay_start'}
                raise LockHandlerError(msg)
            if delay_start <= 0:
                msg = _("The value for %(what)s must be greater " +
                        "than zero (is %(val)r).") % {
                        'val': delay_start, 'what': 'delay_start'}
                raise LockHandlerError(msg)

        if delay_increase is None:
            delay_increase = self.lockretry_delay_increase
        else:
            if not isinstance(delay_increase, Number):
                msg = _("Value %(val)r for %(what)s is not a Number.") % {
                        'val': delay_increase, 'what': 'delay_increase'}
                raise LockHandlerError(msg)
            if delay_increase < 0:
                msg = _("The value for %(what)s must be greater than or " +
                        "equal to zero (is %(val)r).") % {
                        'val': delay_increase, 'what': 'delay_increase'}
                raise LockHandlerError(msg)

        if max_delay is None:
            max_delay = self.lockretry_max_delay
        else:
            if not isinstance(max_delay, Number):
                msg = _("Value %(val)r for %(what)s is not a Number.") % {
                        'val': max_delay, 'what': 'max_delay'}
                raise LockHandlerError(msg)
            if max_delay <= 0:
                msg = _("The value for %(what)s must be greater " +
                        "than zero (is %(val)r).") % {
                        'val': max_delay, 'what': 'max_delay'}
                raise LockHandlerError(msg)
            pass

        if use_pid is None:
            use_pid = self.locking_use_pid
        else:
            use_pid = bool(use_pid)

        if max_age is None:
            max_age = self.max_lockfile_age
        else:
            if not isinstance(max_age, Number):
                msg = _("Value %(val)r for %(what)s is not a Number.") % {
                        'val': max_age, 'what': 'max_age'}
                raise LockHandlerError(msg)
            if max_age <= 0:
                msg = _("The value for %(what)s must be greater " +
                        "than zero (is %(val)r).") % {
                        'val': max_age, 'what': 'max_age'}
                raise LockHandlerError(msg)

        if pid is None:
            pid = os.getpid()
        else:
            pid = int(pid)
            if pid <= 0:
                msg = _("Invalid PID %d given on calling create_lockfile().") % (
                        pid)
                raise LockHandlerError(msg)

        if os.path.isabs(lockfile):
            lockfile = os.path.normpath(lockfile)
        else:
            lockfile = os.path.normpath(os.path.join(self.lockdir, lockfile))

        lockdir = os.path.dirname(lockfile)
        log.debug(_("Trying to lock lockfile %r ...") % (lockfile))
        if self.verbose > 1:
            log.debug(_("Using lock directory %r ...") % (lockdir))

        if not os.path.isdir(lockdir):
            raise LockdirNotExistsError(lockdir)

        if not os.access(lockdir, os.W_OK):
            msg = _("Locking directory %r isn't writeable.") % (lockdir)
            if self.simulate:
                log.error(msg)
            else:
                raise LockdirNotWriteableError(lockdir)

        counter = 0
        delay = delay_start

        fd = None
        time_diff = 0
        start_time = time.time()

        ctime = None
        mtime = None

        # Big loop on trying to create the lockfile
        while fd is None and time_diff < max_delay:

            time_diff = time.time() - start_time
            counter += 1

            if self.verbose > 3:
                log.debug(_("Current time difference: %0.3f seconds.") % (time_diff))
            if time_diff >= max_delay:
                break

            # Try creating lockfile exclusive
            log.debug(_("Try %(try_nr)d on creating lockfile %(lfile)r ...") % {
                    'try_nr': counter, 'lfile': lockfile})
            ctime = datetime.datetime.utcnow()
            fd = self._create_lockfile(lockfile)
            if fd is not None:
                # success, then exit
                break

            # Check for other process, using this lockfile
            if not self.check_lockfile(lockfile, max_age, use_pid):
                # No other process is using this lockfile
                if os.path.exists(lockfile):
                    log.info(_("Removing lockfile %r ...") % (lockfile))
                try:
                    if not self.simulate:
                        os.remove(lockfile)
                except Exception, e:
                    msg = _("Error on removing lockfile %(lfile)r: %(err)s") % {
                            'lfile': lockfile, 'err': e}
                    log.error(msg)
                    time.sleep(delay)
                    delay += delay_increase
                    continue

                fd = self._create_lockfile(lockfile)
                if fd:
                    break

            # No success, then retry later
            if self.verbose > 2:
                log.debug(_("Sleeping for %0.1f seconds."), float(delay))
            time.sleep(delay)
            delay += delay_increase

        # fd is either None, for no success on locking
        if fd is None:
            time_diff = time.time() - start_time
            msg = _("Could not occupy lockfile %(lfile)r after %(secs)0.1f " +
                    "seconds on %(nr)d tries.") % {
                    'lfile': lockfile, 'secs': time_diff, 'nr': counter}
            log.error(msg)
            return None

        # or an int for success
        log.info(_("Got a lock for lockfile %r."), lockfile)
        out = "%d\n" % (pid)
        log.debug(_("Write %(what)r in lockfile %(lfile)r ...") % {
                'what': out, 'lfile': lockfile})
        if not self.simulate:
            os.write(fd, out)
            os.close(fd)

        mtime = datetime.datetime.utcnow()

        lock_object = PbLock(
                lockfile,
                ctime = ctime,
                mtime = mtime,
                fcontent = out,
                simulate = self.simulate,
                appname = self.appname,
                verbose = self.verbose,
                base_dir = self.base_dir,
                use_stderr = self.use_stderr,
        )

        return lock_object

    #--------------------------------------------------------------------------
    def _create_lockfile(self, lockfile):
        """
        Handles exclusive creation of a lockfile.

        @return: a file decriptor of the opened lockfile (if possible),
                 or None, if it isn't.
        @rtype: int or None

        """

        if self.verbose > 1:
            log.debug(_("Trying to open %r exclusive ..."), lockfile)
        if self.simulate:
            log.debug(_("Simulation mode, no real creation of a lockfile."))
            return -1
        fd = None
        try:
            fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0644)
        except OSError, e:
            msg = _("Error on creating lockfile %(lfile)r: %(err)s") % {
                    'lfile': lockfile, 'err': e}
            if e.errno == errno.EEXIST:
                log.debug(msg)
                return None
            else:
                raise LockHandlerError(msg)

        return fd

    #--------------------------------------------------------------------------
    def remove_lockfile(self, lockfile):
        """
        Removing lockfile.

        @param lockfile: the lockfile to remove.
        @type lockfile: str

        @return: the lockfile was removed (or not)
        @rtype: bool

        """

        if os.path.isabs(lockfile):
            lockfile = os.path.normpath(lockfile)
        else:
            lockfile = os.path.normpath(os.path.join(self.lockdir, lockfile))

        if not os.path.exists(lockfile):
            log.debug(_("Lockfile %r to remove doesn't exists."), lockfile)
            return True

        log.info(_("Removing lockfile %r ...") % (lockfile))
        if self.simulate:
            log.debug(_("Simulation mode - lockfile won't removed."))
            return True

        try:
            os.remove(lockfile)
        except Exception, e:
            msg = _("Error on removing lockfile %(lfile)r: %(err)s")
            log.error(msg % {'lfile': lockfile, 'err': e})
            if self.verbose:
                tb = traceback.format_exc()
                log.debug(_("Stacktrace") + ":\n" + tb)
            return False

        return True

    #--------------------------------------------------------------------------
    def check_lockfile(self, lockfile, max_age = None, use_pid = None):
        """
        Checks the validity of the given lockfile.

        If use_pid is True, and there is a PID inside the lockfile, then
        this PID is checked for a running process.
        If use_pid is not True, then the age of the lockfile is checked
        against the parameter max_age.

        @param lockfile: the lockfile to check
        @type lockfile: str
        @param max_age: the maximum age of the lockfile (in seconds), for
                        this lockfile is valid (if use_pid is False).
        @type max_age: int
        @param use_pid: check the content of the lockfile for a PID
                          of a running process
        @type use_pid: bool

        @return: Validity of the lockfile (PID exists and shows to a
                 running process or the lockfile is not too old).
                 Returns False, if the lockfile is not existing, contains an
                 invalid PID or is too old.
        @rtype: bool

        """

        if use_pid is None:
            use_pid = self.locking_use_pid
        else:
            use_pid = bool(use_pid)

        if max_age is None:
            max_age = self.max_lockfile_age
        else:
            if not isinstance(max_age, Number):
                msg = _("Value %(val)r for %(what)s is not a Number.") % {
                        'val': max_age, 'what': 'max_age'}
                raise LockHandlerError(msg)
            if max_age <= 0:
                msg = _("The value for %(what)s must be greater " +
                        "than zero (is %(val)r).") % {
                        'val': max_age, 'what': 'max_age'}
                raise LockHandlerError(msg)

        log.debug(_("Checking lockfile %r ..."), lockfile)

        if not os.path.exists(lockfile):
            if self.verbose > 2:
                log.debug(_("Lockfile %r doesn't exists."), lockfile)
            return False

        if not os.access(lockfile, os.R_OK):
            log.warn(_("No read access for lockfile %r."), lockfile)
            return True

        if not os.access(lockfile, os.W_OK):
            log.warn(_("No write access for lockfile %r."), lockfile)
            return True

        if use_pid:
            pid = self.get_pid_from_file(lockfile, True)
            if pid is None:
                log.warn(_("Unusable lockfile %r."), lockfile)
            else:
                if self.dead(pid):
                    log.warn(_("Process with PID %d is unfortunately dead."), pid)
                    return False
                else:
                    log.debug(_("Process with PID %d is even running."), pid)
                    return True
        fstat = os.stat(lockfile)
        age = time.time() - fstat.st_mtime
        if age >= max_age:
            msg = _("Lockfile %(lfile)r is older than %(max)d seconds (%(age)d seconds).")
            log.debug(msg % {'lfile': lockfile, 'max': max_age, 'age': age})
            return False
        msg = _("Lockfile %(lfile)r is %(age)d seconds old, but not old enough (%(max)d seconds).")
        log.debug(msg % {'lfile': lockfile, 'max': int(max_age), 'age': int(age)})
        return True

    #--------------------------------------------------------------------------
    def get_pid_from_file(self, pidfile, force = False):
        """
        Tries to read the PID of some process from the given file.

        @raise LockHandlerError: if the pidfile could not be read

        @param pidfile: The file, where the PID should be in.
        @type pidfile: str
        @param force: Don't raise an exception, if something is going wrong.
                      Only return None.
        @type force: bool

        @return: PID from pidfile
        @rtype: int (or None)

        """

        if self.verbose > 1:
            log.debug(_("Trying to open pidfile %r ..."), pidfile)
        try:
            fh = open(pidfile, "rb")
        except Exception, e:
            msg = _("Could not open pidfile %r for reading:") % (pidfile)
            msg += " " + str(e)
            if force:
                log.warn(msg)
                return None
            else:
                raise LockHandlerError(str(e))

        content = fh.readline()
        fh.close()

        content = content.strip()
        if content == "":
            msg = _("First line of pidfile %r was empty.") % (pidfile)
            if force:
                log.warn(msg)
                return None
            else:
                raise LockHandlerError(msg)

        pid = None
        try:
            pid = int(content)
        except Exception, e:
            msg = _("Could not interprete %(cont)r as a PID from %(file)r:") % {
                    'cont': content, 'file': pidfile}
            msg += " " + str(e)
            if force:
                log.warn(msg)
                return None
            else:
                raise LockHandlerError(msg)

        if pid <= 0:
            msg = _("Invalid PID %(pid)d in %(file)r found.") % {
                    'pid': pid, 'file': pidfile}
            if force:
                log.warn(msg)
                return None
            else:
                raise LockHandlerError(msg)

        return pid

    #--------------------------------------------------------------------------
    def kill(self, pid, signal = 0):
        """
        Sends a signal to a process.

        @raise OSError: on some unpredictable errors

        @param pid: the PID of the process
        @type pid: int
        @param signal: the signal to send to the process, if the signal is 0
                       (the default), no real signal is sent to the process,
                       it will only checked, whether the process is dead or not
        @type signal: int

        @return: the process is dead or not
        @rtype: bool

        """

        try:
            return os.kill(pid, signal)
        except OSError, e:
            #process is dead
            if e.errno == 3:
                return True
            #no permissions
            elif e.errno == 1:
                return False
            else:
                #reraise the error
                raise

    #--------------------------------------------------------------------------
    def dead(self, pid):
        """
        Gives back, whether the process with the given pid is dead

        @raise OSError: on some unpredictable errors

        @param pid: the PID of the process to check
        @type pid: int

        @return: the process is dead or not
        @rtype: bool

        """

        if self.kill(pid):
            return True

        #maybe the pid is a zombie that needs us to wait4 it
        from os import waitpid, WNOHANG

        try:
            dead = waitpid(pid, WNOHANG)[0]
        except OSError, e:
            #pid is not a child
            if e.errno == 10:
                return False
            else:
                raise

        return dead

#==============================================================================
if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
