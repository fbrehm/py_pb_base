#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: module for some common used error classes
"""

# Standard modules
import errno
import sys

# Own modules
from pb_base.translate import translator

__version__ = '0.2.1'

_ = translator.lgettext
__ = translator.lngettext

if sys.version_info[0] > 2:
    _ = translator.gettext
    __ = translator.ngettext


# =============================================================================
class PbError(Exception):
    """
    Base error class for all other self defined exceptions.
    """

    pass


# =============================================================================
class FunctionNotImplementedError(PbError, NotImplementedError):
    """
    Error class for not implemented functions.
    """

    # -------------------------------------------------------------------------
    def __init__(self, function_name, class_name):
        """
        Constructor.

        @param function_name: the name of the not implemented function
        @type function_name: str
        @param class_name: the name of the class of the function
        @type class_name: str

        """

        self.function_name = function_name
        if not function_name:
            self.function_name = '__unkown_function__'

        self.class_name = class_name
        if not class_name:
            self.class_name = '__unkown_class__'

    # -------------------------------------------------------------------------
    def __str__(self):
        """
        Typecasting into a string for error output.
        """

        msg = _("Function %(func)s() has to be overridden in class '%(cls)s'.")
        return msg % {'func': self.function_name, 'cls': self.class_name}


# =============================================================================
class CallAbstractMethodError(PbError, NotImplementedError):
    """
    Error class indicating, that a uncallable method was called.
    """

    # -------------------------------------------------------------------------
    def __init__(self, classname, method, *args, **kwargs):
        """Constructor."""

        self.classname = classname
        self.method = method
        self.args = args
        self.kwargs = kwargs

    # -------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        msg = _(
            "Invalid call to method %(m)s() in a object of class %(c)r.") + " " _(
            "(probably not overridden?).") % {
            'm': self.method, 'c': self.classname}

        msg += " " + _("Given positional arguments: %r.") % (self.args)
        msg += " " + _("Given keyword arguments: %r.") % (self.kwargs)

        return msg


# =============================================================================
class PbIoTimeoutError(PbError, IOError):
    """
    Special error class indicating a timout error on a read/write operation
    """

    # -------------------------------------------------------------------------
    def __init__(self, strerror, timeout, filename=None):
        """
        Constructor.

        @param strerror: the error message about the operation
        @type strerror: str
        @param timeout: the timout in seconds leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        t_o = None
        try:
            t_o = float(timeout)
        except ValueError:
            pass
        self.timeout = t_o

        if t_o is not None:
            strerror += _(" (timeout after %0.1f secs)") % (t_o)

        if filename is None:
            super(PbIoTimeoutError, self).__init__(errno.ETIMEDOUT, strerror)
        else:
            super(PbIoTimeoutError, self).__init__(
                errno.ETIMEDOUT, strerror, filename)


# =============================================================================
class PbReadTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on reading of a file.
    """

    # -------------------------------------------------------------------------
    def __init__(self, timeout, filename):
        """
        Constructor.

        @param timeout: the timout in seconds leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        strerror = _("Timeout error on reading")
        super(PbReadTimeoutError, self).__init__(strerror, timeout, filename)


# =============================================================================
class PbWriteTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on a writing into a file.
    """

    # -------------------------------------------------------------------------
    def __init__(self, timeout, filename):
        """
        Constructor.

        @param timeout: the timout in seconds leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        strerror = _("Timeout error on writing")
        super(PbWriteTimeoutError, self).__init__(strerror, timeout, filename)


# =============================================================================
class CouldntOccupyLockfileError(PbError):
    """
    Special error class indicating, that a lockfile couldn't coccupied
    after a defined time.
    """

    # -----------------------------------------------------
    def __init__(self, lockfile, duration, tries):
        """
        Constructor.

        @param lockfile: the lockfile, which could't be occupied.
        @type lockfile: str
        @param duration: The duration in seconds, which has lead to this situation
        @type duration: float
        @param tries: the number of tries creating the lockfile
        @type tries: int

        """

        self.lockfile = str(lockfile)
        self.duration = float(duration)
        self.tries = int(tries)

    # -----------------------------------------------------
    def __str__(self):

        return _(
            "Couldn't occupy lockfile %(file)r in %(secs)0.1f seconds with %(tries)d tries.") % {
            'file': self.lockfile, 'secs': self.duration, 'tries': self.tries}

# =============================================================================

if __name__ == "__main__":
    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
