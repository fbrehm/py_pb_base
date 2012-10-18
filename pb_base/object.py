#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for the base object.
          It provides properties and methods used
          by all objects.
"""

# Standard modules
import sys
import os
import logging
import datetime
import traceback

# Third party modules

# Own modules
from pb_base.common import pp

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

__version__ = '0.2.3'

log = logging.getLogger(__name__)

#==============================================================================
class PbBaseObjectError(PbError):
    """
    Base error class useable by all descendand objects.
    """

    pass

#==============================================================================
class PbBaseObject(object):
    """
    Base class for all objects.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
                appname = None,
                verbose = 0,
                version = __version__,
                base_dir = None,
                use_stderr = False,
                initialized = False,
                ):
        """
        Initialisation of the base object.

        Raises an exception on a uncoverable error.

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

        self._appname = None
        """
        @ivar: name of the current running application
        @type: str
        """
        if appname:
            v = str(appname).strip()
            if v:
                self._appname = v
        if not self._appname:
            self._appname = os.path.basename(sys.argv[0])

        self._version = version
        """
        @ivar: version string of the current object or application
        @type: str
        """

        self._verbose = int(verbose)
        """
        @ivar: verbosity level (0 - 9)
        @type: int
        """
        if self._verbose < 0:
            msg = "Wrong verbose level %r, must be >= 0" % (verbose)
            raise ValueError(msg)

        self._initialized = False
        """
        @ivar: initialisation of this object is complete
               after __init__() of this object
        @type: bool
        """

        self._use_stderr = bool(use_stderr)
        """
        @ivar: a flag indicating, that on handle_error() the output should go
               to STDERR, even if logging has initialized logging handlers
        @type: bool
        """

        self._base_dir = base_dir
        """
        @ivar: base directory used for different purposes, must be an existent
               directory. Defaults to directory of current script daemon.py.
        @type: str
        """
        if base_dir:
            if not os.path.exists(base_dir):
                msg = "Base dir '%s' doesn't exists." % (base_dir)
                self.handle_error(msg)
                self._base_dir = None
            elif not os.path.isdir(base_dir):
                msg = "Base dir '%s' isn't a directory." % (base_dir)
                self.handle_error(msg)
                self._base_dir = None
        if not self._base_dir:
            self._base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        self._initialized = bool(initialized)

    #------------------------------------------------------------
    @apply
    def appname():
        doc = "The name of the current running application."
        def fget(self):
            return self._appname
        def fset(self, value):
            if value:
                v = str(value).strip()
                if v:
                    self._appname = v
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def version():
        doc = "The version string of the current object or application."
        def fget(self):
            return self._version
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def verbose():
        doc = "The verbosity level."
        def fget(self):
            return self._verbose
        def fset(self, value):
            v = int(value)
            if v >= 0:
                self._verbose = v
            else:
                log.warn("Wrong verbose level %r, must be >= 0", value)
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def use_stderr():
        doc = "A flag indicating, that on handle_error() the output should go to STDERR."
        def fget(self):
            return self._use_stderr
        def fset(self, value):
            self._use_stderr = bool(value)
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def initialized():
        doc = "The initialisation of this object is complete."
        def fget(self):
            return self._initialized
        def fset(self, value):
            self._initialized = bool(value)
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def base_dir():
        doc = "The base directory used for different purposes."
        def fget(self):
            return self._base_dir
        def fset(self, value):
            if not os.path.exists(value):
                msg = "Base dir '%s' doesn't exists." % (value)
                log.error("Base dir '%s' doesn't exists.", value)
            elif not os.path.isdir(value):
                log.error("Base dir '%s' isn't a directory.", value)
            else:
                self._base_dir = value
        def fdel(self):
            pass
        return property(**locals())

    #--------------------------------------------------------------------------
    def __str__(self):
        """
        Typecasting function for translating object structure
        into a string

        @return: structure as string
        @rtype:  str
        """

        return pp(self.as_dict())

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = self.__dict__
        res = {}
        for key in self.__dict__:
            val = self.__dict__[key]
            if isinstance(val, PbBaseObject):
                res[key] = val.as_dict()
            else:
                res[key] = val
        res['__class_name__'] = self.__class__.__name__

        return res

    #--------------------------------------------------------------------------
    def handle_error(self, error_message = None, exception_name = None,
                        do_traceback = False):
        """
        Handle an error gracefully.

        Print a traceback and continue.

        @param error_message: the error message to display
        @type error_message: str
        @param exception_name: name of the exception class
        @type exception_name: str
        @param do_traceback: allways show a traceback
        @type do_traceback: bool

        """

        msg = 'Exception happened'
        if exception_name:
            msg = exception_name
        if error_message:
            msg += ': ' + str(error_message)
        else:
            msg += '.'

        if log.handlers:
            log.error(msg)
            if do_traceback:
                log.error(traceback.format_exc())

        if self.use_stderr or not log.handlers:
            curdate = datetime.datetime.now()
            curdate_str = "[" + curdate.isoformat(' ') + "]: "
            msg = curdate_str + msg + "\n"
            sys.stderr.write(msg)
            if do_traceback:
                traceback.print_exc()

        return

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
