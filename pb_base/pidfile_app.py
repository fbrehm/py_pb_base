#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for a application object supporting an application,
          which should use a pidfile to ensure a singelton execution
          on the system.
          It provides all from the configured application object with
          additional methods and properties to handle a pidfile.
"""

# Standard modules
import sys
import os
import logging
import datetime

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError

from pb_base.cfg_app import PbCfgAppError
from pb_base.cfg_app import PbCfgApp

from pb_base.pidfile import PidFileError
from pb_base.pidfile import InvalidPidFileError
from pb_base.pidfile import PidFileInUseError
from pb_base.pidfile import PidFile

from pb_base.translate import translator

__version__ = '0.3.4'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

#==============================================================================
class PidfileAppError(PbCfgAppError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#==============================================================================
class PidfileApp(PbCfgApp):
    """
    Base class for all pidfile application objects.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
                appname = None,
                pidfile = None,
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

        @raise PidfileAppError: on a uncoverable error.

        @param appname: name of the current running application
        @type appname: str
        @param pidfile: the filename of the pidfile to use. If not given
                        (what's the default), it tries to detect it from
                        configuration and from given commandline parameters.
        @type pidfile: str
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

        self.pidfile = None
        """
        @ivar: after initialisation the pidfile object to handle it.
        @type: PidFile
        """

        self._default_pidfilename = pidfile
        """
        @ivar: a default filename for a pidfile
        @type: str
        """

        self._pidfilename = None
        """
        @ivar: the resulting filename of the pidfile after evaluating
                configuration and commandline parameters
        @type: str
        """

        self._simulate = False
        """
        @ivar: simulation mode, nothing is really done
        @type: bool
        """

        super(PidfileApp, self).__init__(
                appname = appname,
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

        if not self.pidfilename:
            self._pidfilename = self._default_pidfilename
        if not os.path.isabs(self.pidfilename):
            self._pidfilename = os.path.join(self.base_dir, self.pidfilename)
        if self.verbose > 3:
            log.debug(_("Using pidfile: %r."), self.pidfilename)

        self._simulate = getattr(self.args, 'simulate', False)

        if self.verbose > 1:
            log.debug(_("Initialising PidFile object ..."))
        self.pidfile = PidFile(
                self.pidfilename,
                appname = self.appname,
                verbose = self.verbose,
                base_dir = self.base_dir,
                use_stderr = self.use_stderr,
                simulate = self.simulate,
        )
        self.pidfile.initialized = True

    #------------------------------------------------------------
    @property
    def pidfilename(self):
        """The resulting filename of the pidfile."""
        return self._pidfilename

    #------------------------------------------------------------
    @property
    def simulate(self):
        """Simulation mode, nothing is really done."""
        return self._simulate

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PidfileApp, self).as_dict(short = short)
        res['pidfilename'] = self.pidfilename
        res['simulate'] = self.simulate

        return res

    #--------------------------------------------------------------------------
    def __del__(self):

        self.pidfile = None

    #--------------------------------------------------------------------------
    def init_cfg_spec(self):
        """
        Method to complete the initialisation of the config
        specification file.

        It will called before reading the configuration files and
        their validation.

        """

        super(PidfileApp, self).init_cfg_spec()

        if not u'general' in self.cfg_spec:
            self.cfg_spec[u'general'] = {}

        if not self._default_pidfilename:
            self._default_pidfilename = self.appname + '.pid'

        pidfile_spec = u"string(default = '%s')" % (
                to_unicode_or_bust(self._default_pidfilename))

        if not u'pidfile' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'pidfile'] = pidfile_spec
            self.cfg_spec[u'general'].comments[u'pidfile'].append('')
            self.cfg_spec[u'general'].comments[u'pidfile'].append(
                    u'The filename of the pidfile (absolute or relative' +
                    u' to base_dir).')

    #--------------------------------------------------------------------------
    def perform_config(self):
        """
        Execute some actions after reading the configuration.

        This method should be explicitely called by all perform_config()
        methods in descendant classes.
        """

        super(PidfileApp, self).perform_config()

        if ((not self.pidfilename) and u'general' in self.cfg and
                u'pidfile' in self.cfg[u'general']):
            # Not set by commandline, but set in configuration
            pidfile = to_utf8_or_bust(self.cfg[u'general'][u'pidfile'])
            if pidfile and (pidfile != self._default_pidfilename):
                log.debug(_("Setting pidfile to %r by configuration."),
                        pidfile)
                self._pidfilename = pidfile

    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.

        This method should be explicitely called by all init_arg_parser()
        methods in descendant classes.
        """

        if not self._default_pidfilename:
            self._default_pidfilename = self.appname + '.pid'

        help_txt = _('The name of the pidfile (Default: %s).') % (
                self._default_pidfilename)

        self.arg_parser.add_argument(
                '--pfile', "--pidfile",
                metavar = 'FILE',
                action = 'store',
                dest = "pidfile",
                help = help_txt,
        )

        self.arg_parser.add_argument(
                '-T', '--test', '--simulate', '--dry-run',
                action = "store_true",
                dest = "simulate",
                help = _("Simulation mode, nothing is really done."),
        )

        super(PidfileApp, self).init_arg_parser()

    #--------------------------------------------------------------------------
    def perform_arg_parser(self):
        """
        Execute some actions after parsing the command line parameters.

        This method should be explicitely called by all perform_arg_parser()
        methods in descendant classes.
        """

        super(PidfileApp, self).perform_arg_parser()

        pidfile = getattr(self.args, 'pidfile', None)
        if pidfile and (pidfile != self._default_pidfilename):
            log.debug(_("Setting pidfile to %r by commandline parameter."),
                    pidfile)
            self._pidfilename = pidfile

        self._simulate = getattr(self.args, 'simulate', False)

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

        super(PidfileApp, self).pre_run()

        if self.verbose > 1:
            log.info(_("Creating pidfile %r ..."), self.pidfile.filename)

        try:
            self.pidfile.create()
        except PidFileInUseError, e:
            self.handle_error(str(e), '', False)
            sys.exit(2)
        except PidFileError, e:
            self.handle_error(str(e), '', False)
            sys.exit(3)
        except Exception, e:
            self.handle_error(str(e), e.__class__.__name__, True)
            sys.exit(5)


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
