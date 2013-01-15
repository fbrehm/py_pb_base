#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for a base daemon application object.
          It provides all from the pidfile application object with
          additional methods and properties to daemonize itself.
"""

# Standard modules
import sys
import os
import logging
import signal

from gettext import gettext as _

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

import pb_logging
from pb_logging import valid_syslog_facility
from pb_logging.syslog_handler import PbSysLogHandler

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError

from pb_base.cfg_app import PbCfgAppError

from pb_base.pidfile import PidFileError
from pb_base.pidfile import InvalidPidFileError
from pb_base.pidfile import PidFileInUseError

from pb_base.pidfile_app import PidfileAppError
from pb_base.pidfile_app import PidfileApp

__version__ = '0.3.8'

log = logging.getLogger(__name__)

#--------------------------------------------------------------------------

signal_names = {
    signal.SIGHUP: 'HUP',
    signal.SIGINT: 'INT',
    signal.SIGABRT: 'ABRT',
    signal.SIGTERM: 'TERM',
    signal.SIGKILL: 'KILL',
    signal.SIGUSR1: 'USR1',
    signal.SIGUSR2: 'USR2',
}

#==============================================================================
class PbDaemonError(PidfileAppError):
    """Base error class for all exceptions happened during
    execution this daemon application"""

    pass

#==============================================================================
class PbDaemon(PidfileApp):
    """
    Base class for all daemon application objects.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
                appname = None,
                do_daemonize = True,
                pidfile = None,
                error_log = None,
                facility = None,
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
                cfg_dir = None,
                cfg_stem = None,
                cfg_encoding = 'utf8',
                cfg_spec = None,
                hide_default_config = False,
                need_config_file = False,
                ):
        """
        Initialisation of the daemon object.

        @raise PbDaemonError: on a uncoverable error.

        @param appname: name of the current running application
        @type appname: str
        @param pidfile: the filename of the pidfile to use. If not given
                        (what's the default), it tries to detect it from
                        configuration and from given commandline parameters.
        @type pidfile: str
        @param error_log: the logfile for stderr substitute in daemon mode
        @type error_log: str
        @param do_daemonize: flag indicating, that the application should
                             daemonize itself
        @type do_daemonize: bool
        @param facility: the name of the facility to use to log to syslog
        @type facility: str
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
        @param cfg_dir: directory name under /etc or $HOME respectively, where the
                        normal configuration file should be located.
                        It defaults to self.appname.
                        If no seperate configuration dir should used, give an
                        empty string ('') as directory name.
        @type cfg_dir: str
        @param cfg_stem: the basename of the configuration file without any
                         file extension.
        @type cfg_stem: str
        @param cfg_encoding: encoding character set of the configuration files
                             must be a valid Python encoding
                             (See: http://docs.python.org/library/codecs.html#standard-encodings)
        @type cfg_encoding: str
        @param hide_default_config: hide command line parameter --default-config and
                                    don't execute generation of default config
        @type hide_default_config: bool
        @param need_config_file: through an error message, if none of the default
                                 configuration files were found
        @type need_config_file: bool

        @return: None
        """

        if facility:
            if not facility in valid_syslog_facility:
                raise PbDaemonError(_("Invalid facility name '%s' given.") % (
                        facility))
        else:
            facility = 'daemon'

        self._default_facility_name = facility
        """
        @ivar: the default name of the facility to use to log to syslog
        @type: str
        """

        self._facility_name = None
        """
        @ivar: the name of the facility to use to log to syslog
        @type: str
        """

        self._facility = valid_syslog_facility[self._default_facility_name]
        """
        @ivar: the integer value of the elected syslog facility
        @type: int
        """

        self._do_daemonize = bool(do_daemonize)
        """
        @ivar: flag indicating, that the application should daemonize itself
        @type: bool
        """

        self._default_error_log = error_log
        """
        @ivar: the default logfile for stderr substitute in daemon mode
        @type: str
        """

        self._error_log = None
        """
        @ivar: the logfile for stderr substitute in daemon mode
        @type: str
        """

        self._forced_shutdown = False
        '''
        @ivar: Flag for a forced shutdown. Will be set on exit handler.
        @type: bool
        '''

        super(PbDaemon, self).__init__(
                appname = appname,
                pidfile = pidfile,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
                usage = usage,
                description = description,
                argparse_epilog = argparse_epilog,
                argparse_prefix_chars = argparse_prefix_chars,
                env_prefix = env_prefix,
                cfg_dir = cfg_dir,
                cfg_stem = cfg_stem,
                cfg_encoding = cfg_encoding,
                cfg_spec = cfg_spec,
                hide_default_config = hide_default_config,
                need_config_file = need_config_file,
        )

        self._is_daemon = False
        """
        @ivar: Flag, that the process is runnning as a damon in background
               or in foreground
        @type: bool
        """

        if not self._default_error_log:
            self._default_error_log = 'error.log'

    #--------------------------------------------------------------------------
    @property
    def facility_name(self):
        """The name of the facility to use to log to syslog."""
        return self._facility_name

    #--------------------------------------------------------------------------
    @property
    def facility(self):
        """The integer value of the elected syslog facility."""
        return self._facility

    #--------------------------------------------------------------------------
    @property
    def do_daemonize(self):
        """A flag indicating, that the application should daemonize itself."""
        return self._do_daemonize

    @do_daemonize.setter
    def do_daemonize(self, value):
        self._do_daemonize = bool(value)

    #--------------------------------------------------------------------------
    @property
    def is_daemon(self):
        """
        A flag indicating, that that the process is runnning as a damon
        in background or in foreground.
        """
        return self._is_daemon

    #--------------------------------------------------------------------------
    @property
    def forced_shutdown(self):
        """Flag for a forced shutdown."""
        return self._forced_shutdown

    #--------------------------------------------------------------------------
    @property
    def error_log(self):
        """The logfile for stderr substitute in daemon mode."""
        return self._error_log

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbDaemon, self).as_dict()
        res['facility_name'] = self.facility_name
        res['facility'] = self.facility
        res['do_daemonize'] = self.do_daemonize
        res['is_daemon'] = self.is_daemon
        res['forced_shutdown'] = self.forced_shutdown
        res['error_log'] = self.error_log

        return res

    #--------------------------------------------------------------------------
    def init_cfg_spec(self):
        """
        Method to complete the initialisation of the config
        specification file.

        It will called before reading the configuration files and
        their validation.

        """

        super(PbDaemon, self).init_cfg_spec()

        if not u'general' in self.cfg_spec:
            self.cfg_spec[u'general'] = {}

        daemon_spec = u'boolean(default = %r)' % (self.do_daemonize)

        if not u'do_daemon' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'do_daemon'] = daemon_spec
            self.cfg_spec[u'general'].comments[u'do_daemon'].append('')
            self.cfg_spec[u'general'].comments[u'do_daemon'].append(
                    u'Execute scstadmd as a standalone daemon (default) or ' +
                    u'under control')
            self.cfg_spec[u'general'].comments[u'do_daemon'].append(
                    u'of some kind of daemonisation tool, e.g. supervisor')

        choices = u', '.join(map(lambda x: u"'" + to_unicode_or_bust(x) + u"'",
                sorted(valid_syslog_facility.keys())))
        facility_spec = u"option(%s, default = '%s')" % (choices,
                to_unicode_or_bust(self._default_facility_name))

        if not u'syslog_facility' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'syslog_facility'] = facility_spec
            self.cfg_spec[u'general'].comments[u'syslog_facility'].append('')
            self.cfg_spec[u'general'].comments[u'syslog_facility'].append(
                    u'The syslog facility to use when logging as a daemon.')

        def_errlog = self._default_error_log
        if not def_errlog:
            def_errlog = 'error.log'

        log_spec = u"string(default = '%s')" % (
                to_unicode_or_bust(def_errlog))

        if not u'error_log' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'error_log'] = log_spec
            self.cfg_spec[u'general'].comments[u'error_log'].append('')
            self.cfg_spec[u'general'].comments[u'error_log'].append(
                    u'The logfile for stderr substitute in daemon mode (' +
                    u'absolute or relative to base_dir).')

    #--------------------------------------------------------------------------
    def perform_config(self):
        """
        Execute some actions after reading the configuration.

        This method should be explicitely called by all perform_config()
        methods in descendant classes.
        """

        super(PbDaemon, self).perform_config()

        if u'general' in self.cfg and u'do_daemon' in self.cfg[u'general']:
            self.do_daemonize = self.cfg[u'general'][u'do_daemon']

        if ((not self.facility_name) and u'general' in self.cfg and
                u'syslog_facility' in self.cfg[u'general']):

            # Not set by commandline, but set in configuration
            fac_name  = to_utf8_or_bust(self.cfg[u'general'][u'syslog_facility'])

            if fac_name and (fac_name != self._default_facility_name):
                self._facility_name = fac_name
                self._facility = valid_syslog_facility[fac_name]

        if ((not self.error_log) and u'general' in self.cfg and
                u'error_log' in self.cfg[u'general']):

            # Not set by commandline, but set in configuration
            error_log = to_utf8_or_bust(self.cfg[u'general'][u'error_log'])

            if error_log:
                self._error_log = error_log

    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.

        This method should be explicitely called by all init_arg_parser()
        methods in descendant classes.
        """

        super(PbDaemon, self).init_arg_parser()

        help_txt = _("The syslog facility to use when logging as a daemon " +
                "(default: %s)") % (self._default_facility_name)

        self.arg_parser.add_argument(
                "-F", "--syslog-facility",
                dest = 'syslog_facility',
                choices = sorted(valid_syslog_facility.keys()),
                help = help_txt,
        )

        help_txt = _("Log to console instead to syslog. Don't daemonize " +
                "the application, running in foreground.")

        self.arg_parser.add_argument(
                "-N", "--no-syslog", "--no-daemon",
                action = "store_true",
                dest = "no_syslog",
                help = help_txt,
        )

    #--------------------------------------------------------------------------
    def perform_arg_parser(self):
        """
        Execute some actions after parsing the command line parameters.
        """

        super(PbDaemon, self).perform_arg_parser()

        if self.args.show_default_config:
            return

        fac_name = getattr(self.args, 'syslog_facility', None)
        if fac_name:
            self._facility_name = fac_name
            self._facility = valid_syslog_facility[fac_name]

        no_syslog = getattr(self.args, "no_syslog", False)
        if no_syslog:
            self._do_daemonize = False

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

        no_syslog = getattr(self.args, "no_syslog", False)
        if no_syslog:
            return super(PbDaemon, self).init_logging()

        # create formatter
        format_str = self.appname + ': %(levelname)s - %(message)s'
        if self.verbose:
            if self.verbose > 1:
                format_str = (self.appname +
                              ': %(name)s(%(lineno)d) %(funcName)s() ' +
                              '%(levelname)s - %(message)s')
            else:
                format_str = (self.appname +
                              ': %(name)s %(levelname)s - %(message)s')
        formatter = logging.Formatter(format_str)

        lh_syslog = PbSysLogHandler(
                address = '/dev/log',
                facility = self.facility,
        )
        lh_syslog.setFormatter(formatter)
        root_log.addHandler(lh_syslog)

        return

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

        super(PbDaemon, self).post_init()
        self.initialized = False

        if not self.facility_name:
            self._facility_name = self._default_facility_name

        if not self.error_log:
            self._error_log = self._default_error_log

        self.initialized = True

    #--------------------------------------------------------------------------
    def signal_handler(self, signum, frame):
        """
        Handler as a callback function for getting a signal from somewhere.

        @param signum: the gotten signal number
        @type signum: int
        @param frame: the current stack frame
        @type frame: None or a frame object

        """

        signame = "%d"  % (signum)
        if signum in signal_names:
            signame = signal_names[signum]
        log.info(_("Got a signal %s.") % (signame))

        msg = _("process with PID %(pid)d got signal %(signal)s.") % {
                'pid': os.getpid(), 'signal': signame}
        self.handle_info(msg, self.appname)

        if (signum == signal.SIGUSR1) or (signum == signal.SIGUSR2):
            log.info("Nothing to do on signal USR1 or USR2.")
            return

        # set forced shutdown, except SIGHUP
        forced = False
        if ( (signum == signal.SIGINT) or
                (signum == signal.SIGABRT) or
                (signum == signal.SIGTERM) ):
            log.info("Got a signal for forced shutdown.")
            forced = True

        self._forced_shutdown = forced
        self.exit_action(forced)

    #--------------------------------------------------------------------------
    def exit_action(self, forced = False):
        """
        Method for indicating the application to clearly exit to OS.
        In this implemention only a simple os.exit(0) is done, but this method
        maybe overriden.

        This method will be called by the signal_handler() method.

        @param forced: flag indicating a forced shutdown of the application
                       (in this implemention unused).
        @type forced: bool

        """

        if self.verbose > 2:
            log.debug(_("Exit from %s, so sad ..."), self.appname)

        sys.exit(0)

    #--------------------------------------------------------------------------
    def _daemonize(self):
        """
        The underlaying daemonization process.

        It performs a double fork, closes all standard file handles
        and separates from parent process.

        """

        error_log = self.error_log
        if not os.path.isabs(error_log):
            error_log = os.path.join(self.base_dir, error_log)
        log.debug(_("Using '%s' as error log file."), error_log)

        log_dir = os.path.dirname(error_log)
        log.debug(_("Using '%s' as parent directory of error log file."),
                log_dir)

        if not os.path.exists(log_dir):
            self.handle_error(_("Log directory '%s' doesn't exists.") %
                    (log_dir), self.appname, False)
            sys.exit(6)
        if not os.path.isdir(log_dir):
            self.handle_error(_("Log directory '%s' exists, but is not " +
                    "a directory.") % (log_dir), self.appname, False)
            sys.exit(6)

        se = None
        try:
            se = file(self.error_log, 'a', 0)
        except IOError, e:
            msg = _("Could not open error logfile: %s") % (str(e))
            self.handle_error(msg, self.appname, False)
            sys.exit(7)
        except Exception, e:
            msg = _("Could not open error logfile %(log)s: %(err)s") % {
                    'log': self.error_log, 'err': str(e)}
            self.handle_error(msg, e.__class__.__name__, True)
            sys.exit(8)

        # do the first fork
        log.debug(_("First fork ..."))
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            log.error((_("Fork #1 failed: ") + "%d (%s)"), e.errno, e.strerror)
            sys.exit(1)

        # decouple from parent environment
        os.chdir(self.base_dir)
        os.setsid()
        os.umask(0)

        # do second fork
        log.debug(_("Second fork ..."))
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            log.error((_("Fork #2 failed: ") + "%d (%s)"), e.errno, e.strerror)
            sys.exit(1)

        start_msg = _("%(app)s (v%(ver)s) started as daemon with PID %(pid)d.") % {
                'app': self.appname, 'ver': self.version, 'pid': os.getpid()}

        sys.stdout.write(start_msg + '\n')

        # redirect standard file descriptors
        log.debug(_("Redirect standard file descriptors ..."))
        sys.stdout.flush()
        sys.stderr.flush()

        si = file('/dev/null', 'r')
        so = file('/dev/null', 'a+')
        #se = file(self.error_log, 'a', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        self._is_daemon = True
        log.debug(_("I'm a daemon now - Boooaaaahhh!!!"))
        self.handle_info(start_msg, self.appname)

    #--------------------------------------------------------------------------
    def pre_run(self):
        """
        Code executing before executing the main routine.

        This method should be explicitely called by all pre_run()
        methods in descendant classes.

        It tries to generate the pidfile.
        In case of no success, the application returns with a
        return value of 2.

        """

        super(PbDaemon, self).pre_run()
        self.pidfile.auto_remove = False

        os.chdir(self.base_dir)
        os.umask(0)

        if self.do_daemonize:
            self._daemonize()

        self.pidfile.recreate()
        self.pidfile.auto_remove = True

        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGABRT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGUSR1, self.signal_handler)
        signal.signal(signal.SIGUSR2, self.signal_handler)


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
