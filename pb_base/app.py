#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: The module for a base application object.
          It provides methods for commandline parsing, initialising
          the logging mechanism and running the application.
'''

# Standard modules
import sys
import os
import logging

# Third party modules

# Own modules
from pb_base.common import pp

from pb_logging.colored import ColoredFormatter

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.2.0'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

#==============================================================================
class PbApplicationError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#==============================================================================
class PbApplication(PbBaseObject):
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
        '''
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
        '''

        super(PbApplication, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        self.args = None
        """
        @ivar: an object containing all commandline parameters
               after parsing them
        @type: Namespace
        """

        self._exit_value = 0
        """
        @ivar: return value of the application for exiting with sys.exit().
        @type: int
        """

        self.init_logging()

        if initialized:
            self.initialized = True

    #------------------------------------------------------------
    @apply
    def exit_value():
        doc = "The return value of the application for exiting with sys.exit()."
        def fget(self):
            return self._exit_value
        def fset(self, value):
            v = int(value)
            if v >= 0:
                self._exit_value = v
            else:
                log.warn("Wrong exit_value %r, must be >= 0", value)
        def fdel(self):
            pass
        return property(**locals())

    #--------------------------------------------------------------------------
    def init_logging(self):
        """
        Initialize the logger object.
        It creates a colored loghandler with all output to STDERR.
        Maybe overridden in descendant classes.

        @return: None
        """

        root_log = logging.getLogger()
        root_log.setLevel(logging.INFO)
        if self.verbose:
            root_log.setLevel(logging.DEBUG)

        # create formatter
        format_str = '[%(asctime)s]: ' + self.appname + ': '
        if self.verbose:
            if self.verbose > 1:
                format_str += '%(name)s(%(lineno)d) %(funcName)s() '
            else:
                format_str += '%(name)s'
        format_str += '%(levelname)s - %(message)s'
        color_formatter = ColoredFormatter(format_str)

        # create log handler for console output
        lh_console = logging.StreamHandler(sys.stderr)
        if self.verbose:
            lh_console.setLevel(logging.DEBUG)
        else:
            lh_console.setLevel(logging.INFO)
        lh_console.setFormatter(color_formatter)

        root_log.addHandler(lh_console)

        return

    #--------------------------------------------------------------------------
    def pre_run(self):
        '''
        Dummy function to run before the main routine.
        Could be overwritten by descendant classes.

        '''

        if self.verbose > 1:
            log.info("executing pre_run() ...")

    #--------------------------------------------------------------------------
    def _run(self):
        '''
        Dummy function as main routine.

        MUST be overwritten by descendant classes.

        '''

        raise FunctionNotImplementedError('_run()', self.__class__.__name__)

    #--------------------------------------------------------------------------
    def run(self):
        '''
        The visible start point of this object.
        '''

        try:
            self.pre_run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            sys.exit(98)

        if not self.initialized:
            raise PbApplicationError(("Object '%s' seems not to be completely " +
                                    "initialized.") %
                    (self.__class__.__name__))

        try:
            self._run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            self.exit_value = 99

        if self.verbose > 1:
            log.info("Ending.")

        try:
            self.post_run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            self.exit_value = 97

        sys.exit(self.exit_value)

    #--------------------------------------------------------------------------
    def post_run(self):
        '''
        Dummy function to run after the main routine.
        Could be overwritten by descendant classes.

        '''

        if self.verbose > 1:
            log.info("executing post_run() ...")

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
