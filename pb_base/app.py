#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
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
import platform
import traceback

# Third party modules
import argparse

# Own modules
from pb_base.common import pp

from pb_logging.colored import ColoredFormatter

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

from pb_base.translate import translator

__version__ = '0.6.1'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

argparse._ = translator.lgettext

#----------------------------------------------------------
# _fake_exit flag, for testing
_fake_exit = False

@property
def fake_exit():
    return _fake_exit

@fake_exit.setter
def fake_exit(value):
    _fake_exit = bool(value)

#==============================================================================
class PbApplicationError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#==============================================================================
class FakeExitError(PbApplicationError):
    """
    Special exception class indicating a faked app.exit().

    It can be used in unit tests.

    """

    #--------------------------------------------------------------------------
    def __init__(self, exit_value, msg = None):
        """
        Constructor.

        @param exit_value: the exit value, which should be given back to OS.
        @type exit_value: int
        @param msg: the error message, which should be displayed on exit.
        @type msg: object

        """

        self.exit_value = int(exit_value)
        self.msg = msg

    #--------------------------------------------------------------------------
    def __str__(self):
        """Typecasting into a string for error output."""

        return _("Faked exit to OS. Exit value: %(rv)d, message: %(msg)r") % {
                'rv': self.exit_value, 'msg': self.msg}

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

        @raise PbApplicationError: on a uncoverable error.

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

        self._terminal_has_colors = False
        """
        @ivar: flag, that the current terminal understands color ANSI codes
        @type: bool
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

    #------------------------------------------------------------
    @property
    def exit_value(self):
        """The return value of the application for exiting with sys.exit()."""
        return self._exit_value

    @exit_value.setter
    def exit_value(self, value):
        v = int(value)
        if v >= 0:
            self._exit_value = v
        else:
            log.warn("Wrong exit_value %r, must be >= 0", value)

    #------------------------------------------------------------
    @property
    def exitvalue(self):
        """The return value of the application for exiting with sys.exit()."""
        return self._exit_value

    @exitvalue.setter
    def exitvalue(self, value):
        v = int(value)
        if v >= 0:
            self._exit_value = v
        else:
            log.warn("Wrong exit_value %r, must be >= 0", value)

    #------------------------------------------------------------
    @property
    def usage(self):
        """The usage text used on argparse."""
        return self._usage

    #------------------------------------------------------------
    @property
    def description(self):
        """A short text describing the application."""
        return self._description

    #------------------------------------------------------------
    @property
    def argparse_epilog(self):
        """An epilog displayed at the end of the argparse help screen."""
        return self._argparse_epilog

    #------------------------------------------------------------
    @property
    def argparse_prefix_chars(self):
        """The set of characters that prefix optional arguments."""
        return self._argparse_prefix_chars

    #------------------------------------------------------------
    @property
    def terminal_has_colors(self):
        """A flag, that the current terminal understands color ANSI codes."""
        return self._terminal_has_colors

    #------------------------------------------------------------
    @property
    def env_prefix(self):
        """A prefix for environment variables to detect them."""
        return self._env_prefix

    #------------------------------------------------------------
    @property
    def usage_term(self):
        """The localized version of 'usage: '"""
        return _('usage: ')

    #------------------------------------------------------------
    @property
    def usage_term_len(self):
        """The length of the localized version of 'usage: '"""
        return len(self.usage_term)

    #--------------------------------------------------------------------------
    def exit(self, retval = -1, msg = None, trace = False):
        """
        Universal method to call sys.exit(). If fake_exit is set, a
        FakeExitError exception is raised instead (useful for unittests.)

        @param retval: the return value to give back to theoperating system
        @type retval: int
        @param msg: a last message, which should be emitted before exit.
        @type msg: str
        @param trace: flag to output a stack trace before exiting
        @type trace: bool

        @return: None

        """

        retval = int(retval)
        trace = bool(trace)

        ssys.stderr.write("Blub\n")

        root_log = logging.getLogger()
        has_handlers = False
        if root_log.handlers:
            has_handlers = True

        if msg:
            if has_handlers:
                if retval:
                    log.error(msg)
                else:
                    log.info(msg)
            if self.use_stderr or not has_handlers:
                sys.stderr.write(str(msg) + "\n")

        if trace:
            if has_handlers:
                if retval:
                    log.error(traceback.format_exc())
                else:
                    log.info(traceback.format_exc())
            if self.use_stderr or not has_handlers:
                traceback.print_exc()

        if fake_exit:
            raise FakeExitError(retval, msg)
        else:
            sys.exit(retval)

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbApplication, self).as_dict(short = short)
        res['exit_value'] = self.exit_value
        res['usage'] = self.usage
        res['description'] = self.description
        res['argparse_epilog'] = self.argparse_epilog
        res['argparse_prefix_chars'] = self.argparse_prefix_chars
        res['terminal_has_colors'] = self.terminal_has_colors
        res['env_prefix'] = self.env_prefix

        return res

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
        format_str = ''
        if self.verbose > 1:
            format_str = '[%(asctime)s]: '
        format_str += self.appname + ': '
        if self.verbose:
            if self.verbose > 1:
                format_str += '%(name)s(%(lineno)d) %(funcName)s() '
            else:
                format_str += '%(name)s '
        format_str += '%(levelname)s - %(message)s'
        formatter = None
        if self.terminal_has_colors:
            formatter = ColoredFormatter(format_str)
        else:
            formatter = logging.Formatter(format_str)

        # create log handler for console output
        lh_console = logging.StreamHandler(sys.stderr)
        if self.verbose:
            lh_console.setLevel(logging.DEBUG)
        else:
            lh_console.setLevel(logging.INFO)
        lh_console.setFormatter(formatter)

        root_log.addHandler(lh_console)

        return

    #--------------------------------------------------------------------------
    def terminal_can_color(self):
        """
        Method to detect, whether the current terminal (stdout and stderr)
        is able to perform ANSI color sequences.

        @return: both stdout and stderr can perform ANSI color sequences
        @rtype: bool

        """

        cur_term = ''
        if 'TERM' in os.environ:
            cur_term = os.environ['TERM'].lower().strip()

        ansi_term = False
        #env_term_has_colors = False
        #re_term = re.compile(r'^(?:ansi|linux.*|screen|[xeak]term.*|gnome.*|rxvt.*|interix)$')
        #if cur_term and re_term.search(cur_term):
        #    env_term_has_colors = True
        if cur_term and cur_term == 'ansi':
            ansi_term = True

        has_colors = True
        for handle in [sys.stdout, sys.stderr]:
            if (hasattr(handle, "isatty") and handle.isatty()) or ansi_term:
                if (platform.system() == 'Windows' and not ansi_term):
                    has_colors = False
            else:
                has_colors = False

        return has_colors

    #--------------------------------------------------------------------------
    def post_init(self):
        """
        Method to execute before calling run(). Here could be done some
        finishing actions after reading in commandline parameters,
        configuration a.s.o.

        This method could be overwritten by descendant classes, these
        methhods should allways include a call to post_init() of the
        parent class.

        """

        self.perform_arg_parser()
        self.init_logging()

        self.initialized = True

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
    def __call__(self):
        """
        Helper method to make the resulting object callable, e.g.::

            app = PbApplication(...)
            app()

        @return: None

        """

        self.run()

    #--------------------------------------------------------------------------
    def run(self):
        """
        The visible start point of this object.

        @return: None

        """

        if not self.initialized:
            self.handle_error(_("The application is not complete initialized."),
                    '', True)
            self.exit(9)

        try:
            self.pre_run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            self.exit(98)

        if not self.initialized:
            raise PbApplicationError(_("Object '%s' seems not to be completely " +
                                    "initialized.") %
                    (self.__class__.__name__))

        try:
            self._run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            self.exit_value = 99

        if self.verbose > 1:
            log.info(_("Ending."))

        try:
            self.post_run()
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            self.exit_value = 97

        self.exit(self.exit_value)

    #--------------------------------------------------------------------------
    def post_run(self):
        """
        Dummy function to run after the main routine.
        Could be overwritten by descendant classes.

        """

        if self.verbose > 1:
            log.info(_("executing post_run() ..."))

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

        general_group = self.arg_parser.add_argument_group(_('General options'))
        general_group.add_argument(
                '--color',
                action = "store",
                dest = 'color',
                const = 'yes',
                default = 'auto',
                nargs = '?',
                choices = ['yes', 'no', 'auto'],
                help = _("Use colored output for messages."),
        )
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
                "-V", '--version',
                action = 'version',
                version = (_('Version of %%(prog)s: %s') % (self.version)),
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

        want_color = 'auto'
        if want_color is None:
            want_color = 'yes'
        if want_color == 'yes':
            self._terminal_has_colors = True
        elif want_color == 'no':
            self._terminal_has_colors = False
        else:
            self._terminal_has_colors = self.terminal_can_color()

        self.args = self.arg_parser.parse_args()

        if self.args.usage:
            self.arg_parser.print_usage(sys.stdout)
            self.exit(0)

        if self.args.verbose > self.verbose:
            self.verbose = self.args.verbose

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

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
