#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a base application object.
          It provides methods for commandline parsing, initialising
          the logging mechanism, read in all application spcific
          environment variables and running the application.
"""

# Standard modules
import sys
import os
import logging
import re

from gettext import gettext as _

# Third party modules
import argparse

# Own modules
from pb_base.common import pp

from pb_logging.colored import ColoredFormatter

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

__version__ = '0.4.2'

log = logging.getLogger(__name__)

#==============================================================================
class PbApplicationError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#==============================================================================
class PbApplication(PbBaseObject):
    """
    Base class for all application objects.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
                appname = None,
                verbose = 0,
                version = __version__,
                base_dir = None,
                use_stderr = False,
                initialized = False,
                usage = None,
                description = None,
                argparse_epilog = None,
                argparse_prefix_chars = '-',
                env_prefix = None,
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
        @param usage: usage text used on argparse
        @type usage: str
        @param description: a short text describing the application
        @type description: str
        @param argparse_epilog: an epilog displayed at the end
                                of the argparse help screen
        @type argparse_epilog: str
        @param argparse_prefix_chars: The set of characters that prefix
                                      optional arguments.
        @type argparse_prefix_chars: str
        @param env_prefix: a prefix for environment variables to find them
                           and assign them to the current application,
                           if not given, the appname in uppercase letters
                           and a trailing underscore is assumed.
        @type env_prefix: str

        @return: None
        """

        super(PbApplication, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        self.arg_parser = None
        """
        @ivar: argparser object to parse commandline parameters
        @type: argparse.ArgumentParser
        """

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

        self._usage = usage
        """
        @ivar: usage text used on argparse
        @type: str
        """

        self._description = description
        """
        @ivar: a short text describing the application
        @type: str
        """

        self._argparse_epilog = argparse_epilog
        """
        @ivar: an epilog displayed at the end of the argparse help screen
        @type: str
        """

        self._argparse_prefix_chars = argparse_prefix_chars
        """
        @ivar: The set of characters that prefix optional arguments.
        @type: str
        """

        self.env = {}
        """
        @ivar: a dictionary with all application specifiv environment variables,
               they will detected by the env_prefix property of this object,
               and their names will transformed before saving their values in
               self.env by removing the env_prefix from the variable name.
        @type: dict
        """

        self._env_prefix = self.appname.upper() + '_'
        """
        @ivar: a prefix for environment variables to detect them and to assign
               their transformed names and their values in self.env
        @type: str
        """
        if env_prefix:
            ep = str(env_prefix).strip()
            if not ep:
                msg = "Invalid env_prefix %r given - it may not be empty." % (
                        env_prefix)
                raise PbApplicationError(msg)
            match = re.search(r'^[a-z0-9][a-z0-9_]*$', ep, re.IGNORECASE)
            if not match:
                msg = ("Invalid characters found in env_prefix %r, only " +
                        "alphanumeric characters and digits and underscore " +
                        "(this not as the first character) are allowed.") % (
                        env_prefix)
                raise PbApplicationError(msg)
            self._env_prefix = ep

        self._init_arg_parser()
        self._perform_arg_parser()

        self._init_env()
        self._perform_env()

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

    #------------------------------------------------------------
    @apply
    def usage():
        doc = "The usage text used on argparse."
        def fget(self):
            return self._usage
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def description():
        doc = "A short text describing the application."
        def fget(self):
            return self._description
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def argparse_epilog():
        doc = "An epilog displayed at the end of the argparse help screen."
        def fget(self):
            return self._argparse_epilog
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def argparse_prefix_chars():
        doc = "The set of characters that prefix optional arguments."
        def fget(self):
            return self._argparse_prefix_chars
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #------------------------------------------------------------
    @apply
    def env_prefix():
        doc = "A prefix for environment variables to detect them."
        def fget(self):
            return self._env_prefix
        def fset(self, value):
            pass
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
                format_str += '%(name)s '
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
        """
        Dummy function to run before the main routine.
        Could be overwritten by descendant classes.

        """

        if self.verbose > 1:
            log.info("executing pre_run() ...")

    #--------------------------------------------------------------------------
    def _run(self):
        """
        Dummy function as main routine.

        MUST be overwritten by descendant classes.

        """

        raise FunctionNotImplementedError('_run()', self.__class__.__name__)

    #--------------------------------------------------------------------------
    def run(self):
        """
        The visible start point of this object.
        """

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
        """
        Dummy function to run after the main routine.
        Could be overwritten by descendant classes.

        """

        if self.verbose > 1:
            log.info("executing post_run() ...")

    #--------------------------------------------------------------------------
    def _init_arg_parser(self):
        """
        Local called method to initiate the argument parser.

        @raise PbApplicationError: on some errors

        """

        self.arg_parser = argparse.ArgumentParser(
            prog = self.appname,
            description = self.description,
            usage = self.usage,
            epilog = self.argparse_epilog,
            prefix_chars = self.argparse_prefix_chars,
            add_help = False,
        )

        self.init_arg_parser()

        general_group = self.arg_parser.add_argument_group('General options:')
        general_group.add_argument(
                "-v", "--verbose",
                action = "count",
                dest = 'verbose',
                help = _('Increase the verbosity level'),
        )
        general_group.add_argument(
                "-h", "--help",
                action = 'help',
                dest = 'help',
                help = _('Show this help message and exit')
        )
        general_group.add_argument(
                "--usage",
                action = 'store_true',
                dest = 'usage',
                help = _("Display brief usage message and exit")
        )
        general_group.add_argument(
                "-V", "--version",
                action = 'store_true',
                dest = 'version',
                help = _("Show program's version number and exit")
        )

    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Public available method to initiate the argument parser.

        Note::
             avoid adding the general options '--verbose', '--help', '--usage'
             and '--version'. These options are allways added after executing
             this method.

        Descendant classes may override this method.

        """

        pass

    #--------------------------------------------------------------------------
    def _perform_arg_parser(self):
        """
        Underlaying method for parsing arguments.
        """

        self.args = self.arg_parser.parse_args()

        if self.args.version:
            msg = self.version
            if self.args.verbose:
                msg = _("Version of %s: %s") % (self.appname, self.version)
            sys.stdout.write(msg + "\n")
            sys.exit(0)

        if self.args.usage:
            self.arg_parser.print_usage(sys.stdout)
            sys.exit(0)

        if self.args.verbose > self.verbose:
            self.verbose = self.args.verbose

        self.perform_arg_parser()

    #--------------------------------------------------------------------------
    def perform_arg_parser(self):
        """
        Public available method to execute some actions after parsing
        the command line parameters.

        Descendant classes may override this method.
        """

        pass

    #--------------------------------------------------------------------------
    def _init_env(self):
        """
        Initialization of self.env by application specific environment
        variables.

        It calls self.init_env(), after it has done his job.

        """

        for (key, value) in os.environ.items():

            if not key.startswith(self.env_prefix):
                continue

            newkey = key.replace(self.env_prefix, '', 1)
            self.env[newkey] = value

        self.init_env()

    #--------------------------------------------------------------------------
    def init_env(self):
        """
        Public available method to initiate self.env additional to the implicit
        initialization done by this module.
        Maybe it can be used to import environment variables, their
        names not starting with self.env_prefix.

        Currently a dummy method, which ca be overriden by descendant classes.

        """

        pass

    #--------------------------------------------------------------------------
    def _perform_env(self):
        """
        Method to do some useful things with the found environment.

        It calls self.perform_env(), after it has done his job.

        """

        # try to detect verbosity level from environment
        if 'VERBOSE' in self.env and self.env['VERBOSE']:
            v = 0
            try:
                v = int(self.env['VERBOSE'])
            except ValueError:
                v = 1
            if v > self.verbose:
                self.verbose = v

        self.perform_env()

    #--------------------------------------------------------------------------
    def perform_env(self):
        """
        Public available method to perform found environment variables after
        initialization of self.env.

        Currently a dummy method, which ca be overriden by descendant classes.

        """

        pass

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
