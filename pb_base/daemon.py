#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a base daemon application object.
          It provides all from the pidfile application object with
          additional methods and properties to daemonize itself.
"""

# Standard modules
import sys
import os
import logging

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

__version__ = '0.1.1'

log = logging.getLogger(__name__)

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
                pidfile = None,
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
        )

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

        choices = u', '.join(map(lambda x: u"'" + to_unicode_or_bust(x) + u"'",
                sorted(valid_syslog_facility.keys())))
        facility_spec = u"option(%s, default = '%s')" % (choices,
                to_unicode_or_bust(self._default_facility_name))

        if not u'syslog_facility' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'syslog_facility'] = facility_spec
            self.cfg_spec[u'general'].comments[u'syslog_facility'].append('')
            self.cfg_spec[u'general'].comments[u'syslog_facility'].append(
                    u'The syslog facility to use when logging as a daemon.')

    #--------------------------------------------------------------------------
    def perform_config(self):
        """
        Execute some actions after reading the configuration.

        This method should be explicitely called by all perform_config()
        methods in descendant classes.
        """

        super(PbDaemon, self).perform_config()

        if ((not self.facility_name) and u'general' in self.cfg and
                u'syslog_facility' in self.cfg[u'general']):

            # Not set by commandline, but set in configuration
            fac_name  = to_utf8_or_bust(self.cfg[u'general'][u'syslog_facility'])

            if fac_name and (fac_name != self._default_facility_name):
                self._facility_name = fac_name
                self._facility = valid_syslog_facility[fac_name]

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

        self.arg_parser.add_argument(
                "-N", "--no-syslog",
                action = "store_true",
                dest = "no_syslog",
                help = _("Log to console instead to syslog."),
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

        self.initialized = True


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
