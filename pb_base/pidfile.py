#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2016 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for a pidfile object.
          It provides methods to define, check,  create
          and remove a pidfile.
"""

# Standard modules
import sys
import os
import logging
import re
import signal
import errno

# Third party modules
import six
from six import reraise

# Own modules

from pb_base.errors import PbReadTimeoutError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

from pb_base.common import to_utf8_or_bust

from pb_base.translate import pb_gettext, pb_ngettext

__version__ = '0.5.4'

log = logging.getLogger(__name__)

_ = pb_gettext
__ = pb_ngettext


# =============================================================================
class PidFileError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    handling a pidfile."""

    pass


# =============================================================================
class InvalidPidFileError(PidFileError):
    """An error class indicating, that the given pidfile is unusable"""

    def __init__(self, pidfile, reason=None):
        """
        Constructor.

        @param pidfile: the filename of the invalid pidfile.
        @type pidfile: str
        @param reason: the reason, why the pidfile is invalid.
        @type reason: str

        """

        self.pidfile = pidfile
        self.reason = reason

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        msg = None
        if self.reason:
            msg = _(
                "Invalid pidfile '%(pidfile)s' given: %(reason)s") % {
                'pidfile': self.pidfile, 'reason': self.reason}
        else:
            msg = _("Invalid pidfile %r given.") % (self.pidfile)

        return msg


# =============================================================================
class PidFileInUseError(PidFileError):
    """
    An error class indicating, that the given pidfile is in use
    by another application.
    """

    def __init__(self, pidfile, pid):
        """
        Constructor.

        @param pidfile: the filename of the pidfile.
        @type pidfile: str
        @param pid: the PID of the process owning the pidfile
        @type pid: int

        """

        self.pidfile = pidfile
        self.pid = pid

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        msg = _(
            "The pidfile '%(pf)s is currently in use by the application with the PID %(pid)d.") % {
            'pf': self.pidfile, 'pid': self.pid}

        return msg


# =============================================================================
class PidFile(PbBaseObject):
    """
    Base class for a pidfile object.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self, filename, auto_remove=True, appname=None, verbose=0,
            version=__version__, base_dir=None, use_stderr=False,
            initialized=False, simulate=False, timeout=10):
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
        @param timeout: timeout in seconds for IO operations on pidfile
        @type timeout: int

        @return: None
        """

        self._created = False
        """
        @ivar: the pidfile was created by this current object
        @type: bool
        """

        super(PidFile, self).__init__(
            appname=appname,
            verbose=verbose,
            version=version,
            base_dir=base_dir,
            use_stderr=use_stderr,
            initialized=False,
        )

        if not filename:
            raise ValueError(_('No filename given on initializing PidFile object.'))

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

        self._timeout = int(timeout)
        """
        @ivar: timeout in seconds for IO operations on pidfile
        @type: int
        """

    # -----------------------------------------------------------
    @property
    def filename(self):
        """The filename of the pidfile."""
        return self._filename

    # -----------------------------------------------------------
    @property
    def auto_remove(self):
        """Remove the self created pidfile on destroying the current object."""
        return self._auto_remove

    @auto_remove.setter
    def auto_remove(self, value):
        self._auto_remove = bool(value)

    # -----------------------------------------------------------
    @property
    def simulate(self):
        """Simulation mode."""
        return self._simulate

    # -----------------------------------------------------------
    @property
    def created(self):
        """The pidfile was created by this current object."""
        return self._created

    # -----------------------------------------------------------
    @property
    def timeout(self):
        """The timeout in seconds for IO operations on pidfile."""
        return self._timeout

    # -----------------------------------------------------------
    @property
    def parent_dir(self):
        """The directory containing the pidfile."""
        return os.path.dirname(self.filename)

    # -------------------------------------------------------------------------
    def as_dict(self, short=False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PidFile, self).as_dict(short=short)
        res['filename'] = self.filename
        res['auto_remove'] = self.auto_remove
        res['simulate'] = self.simulate
        res['created'] = self.created
        res['timeout'] = self.timeout
        res['parent_dir'] = self.parent_dir

        return res

    # -------------------------------------------------------------------------
    def __repr__(self):
        """Typecasting into a string for reproduction."""

        out = "<%s(" % (self.__class__.__name__)

        fields = []
        fields.append("filename=%r" % (self.filename))
        fields.append("auto_remove=%r" % (self.auto_remove))
        fields.append("appname=%r" % (self.appname))
        fields.append("verbose=%r" % (self.verbose))
        fields.append("base_dir=%r" % (self.base_dir))
        fields.append("use_stderr=%r" % (self.use_stderr))
        fields.append("initialized=%r" % (self.initialized))
        fields.append("simulate=%r" % (self.simulate))
        fields.append("timeout=%r" % (self.timeout))

        out += ", ".join(fields) + ")>"
        return out

    # -------------------------------------------------------------------------
    def __del__(self):
        """Destructor. Removes the pidfile, if it was created by ourselfes."""

        if not self.created:
            return

        if not os.path.exists(self.filename):
            if self.verbose > 3:
                log.debug(
                    _("Pidfile '%s' doesn't exists, not removing."), self.filename)
            return

        if not self.auto_remove:
            if self.verbose > 3:
                log.debug(
                    _("Auto removing disabled, don't deleting '%s'."),
                    self.filename)
            return

        if self.verbose > 1:
            log.debug(_("Removing pidfile '%s' ..."), self.filename)
        if self.simulate:
            if self.verbose > 1:
                log.debug(_("Just kidding .."))
            return
        try:
            os.remove(self.filename)
        except OSError as e:
            log.err(
                _("Could not delete pidfile %(file)r: %(err)s"),
                self.filename, str(e))
        except Exception as e:
            self.handle_error(str(e), e.__class__.__name__, True)

    # -------------------------------------------------------------------------
    def create(self, pid=None):
        """
        The main method of this class. It tries to write the PID of the process
        into the pidfile.

        @param pid: the pid to write into the pidfile. If not given, the PID of
                    the current process will taken.
        @type pid: int

        """

        if pid:
            pid = int(pid)
            if pid <= 0:
                msg = _(
                    "Invalid PID %(pid)d for creating pidfile %(pidfile)r given.") % {
                    'pid': pid, 'pidfile': self.filename}
                raise PidFileError(msg)
        else:
            pid = os.getpid()

        if self.check():

            log.info(_("Deleting pidfile '%s' ..."), self.filename)
            if self.simulate:
                log.debug(_("Just kidding .."))
            else:
                try:
                    os.remove(self.filename)
                except OSError as e:
                    raise InvalidPidFileError(self.filename, str(e))

        if self.verbose > 1:
            log.debug(_("Trying opening '%s' exclusive ..."), self.filename)

        if self.simulate:
            log.debug(
                _("Simulation mode - don't real writing in '%s'."), self.filename)
            self._created = True
            return

        fd = None
        try:
            fd = os.open(
                self.filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except OSError as e:
            error_tuple = sys.exc_info()
            msg = _(
                "Error on creating pidfile '%(pidfile)s': %(err)s") % {
                'pidfile': self.filename, 'err': str(e)}
            reraise(PidFileError, msg, error_tuple[2])

        if self.verbose > 2:
            log.debug(_(
                "Writing %(pid)d into '%(pidfile)s' ...") % {
                'pid': pid, 'pidfile': self.filename})

        out = "%d\n" % (pid)
        if six.PY3:
            out = to_utf8_or_bust(out)
        try:
            os.write(fd, out)
        finally:
            os.close(fd)

        self._created = True

    # -------------------------------------------------------------------------
    def recreate(self, pid=None):
        """
        Rewrites an even created pidfile with the current PID.

        @param pid: the pid to write into the pidfile. If not given, the PID of
                    the current process will taken.
        @type pid: int

        """

        if not self.created:
            msg = _("Calling recreate() on a not self created pidfile.")
            raise PidFileError(msg)

        if pid:
            pid = int(pid)
            if pid <= 0:
                msg = _(
                    "Invalid PID %(pid)d for creating pidfile %(pidfile)r given.") % {
                    'pid': pid, 'pidfile': self.filename}
                raise PidFileError(msg)
        else:
            pid = os.getpid()

        if self.verbose > 1:
            log.debug(_("Trying opening '%s' for recreate ..."), self.filename)

        if self.simulate:
            log.debug(
                _("Simulation mode - don't real writing in '%s'."), self.filename)
            return

        fh = None
        try:
            fh = open(self.filename, 'w')
        except OSError as e:
            error_tuple = sys.exc_info()
            msg = _(
                "Error on recreating pidfile '%(pidfile)s': %(err)s") % {
                'pidfile': self.filename, 'err': str(e)}
            reraise(PidFileError, msg, error_tuple[2])

        if self.verbose > 2:
            log.debug(_(
                "Writing %(pid)d into '%(pidfile)s' ...") % {
                'pid': pid, 'pidfile': self.filename})

        try:
            fh.write("%d\n" % (pid))
        finally:
            fh.close()

    # -------------------------------------------------------------------------
    def check(self):
        """
        This methods checks the usability of the pidfile.
        If the method doesn't raise an exception, the pidfile is usable.

        It returns, whether the pidfile exist and can be deleted or not.

        @raise InvalidPidFileError: if the pidfile is unusable
        @raise PidFileInUseError: if the pidfile is in use by another application
        @raise PbReadTimeoutError: on timeout reading an existing pidfile
        @raise OSError: on some other reasons, why the existing pidfile
                        couldn't be read

        @return: the pidfile exists, but can be deleted - or it doesn't
                 exists.
        @rtype: bool

        """

        if not os.path.exists(self.filename):
            if not os.path.exists(self.parent_dir):
                reason = _(
                    "Pidfile parent directory '%s' doesn't exists.") % (
                    self.parent_dir)
                raise InvalidPidFileError(self.filename, reason)
            if not os.path.isdir(self.parent_dir):
                reason = _(
                    "Pidfile parent directory '%s' is not a directory.") % (
                    self.parent_dir)
                raise InvalidPidFileError(self.filename, reason)
            if not os.access(self.parent_dir, os.X_OK):
                reason = _(
                    "No write access to pidfile parent directory '%s'.") % (
                    self.parent_dir)
                raise InvalidPidFileError(self.filename, reason)

            return False

        if not os.path.isfile(self.filename):
            reason = _("It is not a regular file.")
            raise InvalidPidFileError(self.filename, self.parent_dir)

        # ---------
        def pidfile_read_alarm_caller(signum, sigframe):
            """
            This nested function will be called in event of a timeout.

            @param signum: the signal number (POSIX) which happend
            @type signum: int
            @param sigframe: the frame of the signal
            @type sigframe: object
            """

            return PbReadTimeoutError(self.timeout, self.filename)

        if self.verbose > 1:
            log.debug(_("Reading content of pidfile %r ..."), self.filename)

        signal.signal(signal.SIGALRM, pidfile_read_alarm_caller)
        signal.alarm(self.timeout)

        content = ''
        fh = None

        try:
            fh = open(self.filename, 'r')
            for line in fh.readlines():
                content += line
        finally:
            if fh:
                fh.close()
            signal.alarm(0)

        # Performing content of pidfile

        pid = None
        line = content.strip()
        match = re.search(r'^\s*(\d+)\s*$', line)
        if match:
            pid = int(match.group(1))
        else:
            msg = _("No useful information found in pidfile %(file)r: %(line)r")
            log.warn(msg % {'file': self.filename, 'line': line})
            return True

        if self.verbose > 1:
            msg = _("Trying check for process with PID %d ...") % (pid)
            log.debug(msg)

        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                log.info(_("Process with PID %d anonymous died."), pid)
                return True
            elif err.errno == errno.EPERM:
                error_tuple = sys.exc_info()
                msg = _("No permission to signal the process %d ...") % (pid)
                reraise(PidFileError, msg, error_tuple[2])
            else:
                error_tuple = sys.exc_info()
                msg = _("Got a %(ecls)s: %(msg)s.") % {
                    'ecls': err.__class__.__name__, 'msg': err}
                reraise(PidFileError, msg, error_tuple[2])
        else:
            raise PidFileInUseError(self.filename, pid)

        return False


# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
