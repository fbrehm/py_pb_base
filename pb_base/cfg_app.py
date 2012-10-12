#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: The module for a base configured application object.
          It provides all from the base application object with additional
          methods and properties to read different configuration files.
'''

# Standard modules
import sys
import os
import logging

from textwrap import dedent
from gettext import gettext as _
from cStringIO import StringIO

# Third party modules
from configobj import ConfigObj
from validate import Validator
from validate import ValidateError

# Own modules
from pb_base.common import pp, to_unicode_or_bust

from pb_base.rec_dict import RecursiveDictionary

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError
from pb_base.app import PbApplication

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010-2012 by profitbricks.com'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.4.0'
__license__ = 'GPL3'

log = logging.getLogger(__name__)

#==============================================================================
class PbCfgAppError(PbApplicationError):
    """Base error class for all exceptions happened during
    execution this configured application"""

    pass

#==============================================================================
class PbCfgApp(PbApplication):
    """
    Base class for all configured application objects.
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
                cfg_encoding = 'utf8',
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
        @param cfg_encoding: encoding character set of the configuration files
                             must be a valid Python encoding
                             (See: http://docs.python.org/library/codecs.html#standard-encodings)
        @type cfg_encoding: str

        @return: None
        '''

        self._cfg_encoding = cfg_encoding
        """
        @ivar: encoding character set of the configuration files
        @type: str
        """

        super(PbCfgApp, self).__init__(
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
        )

        self.cfg = RecursiveDictionary()
        """
        @ivar: a dict containing all configuration parameters read in from
               different configuration files and other sources.
        @type: RecursiveDictionary
        """

        self.cfg_files = []
        """
        @ivar: all configuration files to use for this application in the order
               of reading in them - the file with the lowest priority first,
               this file with the highest priority at last.
        @type: list of str
        """
        self.init_cfgfiles()

        self.cfg_spec = ''
        """
        @ivar: a specification of the configuration, which should
               be found in the configuration files.
               See: http://www.voidspace.org.uk/python/configobj.html#validation
               how to write such a specification.
        @type: str
        """
        self._init_cfg_spec()

        self._read_config()

    #------------------------------------------------------------
    @apply
    def cfg_encoding():
        doc = "The encoding character set of the configuration files."
        def fget(self):
            return self._cfg_encoding
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return property(**locals())

    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.

        This method should be explicitely called by all init_arg_parser()
        methods in descendant classes.
        """

        self.arg_parser.add_argument(
                "-C", "--cfgfile", "--cfg-file", "--config",
                metavar = "FILE",
                dest = "cfg_file",
                help = _("Configuration file to use additional to the " +
                        "standard configuration files."),
        )

        self.arg_parser.add_argument(
                "--cfg-encoding",
                metavar = "ENCODING",
                dest = "cfg_encoding",
                default = self.cfg_encoding,
                help = _("The encoding character set of the configuration files")
        )

    #--------------------------------------------------------------------------
    def perform_arg_parser(self):
        """
        Execute some actions after parsing the command line parameters.

        This method should be explicitely called by all perform_arg_parser()
        methods in descendant classes.
        """

        # Store a maybe other character set of configuration files
        # in self.cfg_encoding
        enc = getattr(self.args, 'cfg_encoding', None)
        if enc:
            enc = enc.lower()
            if enc != self.cfg_encoding:
                self._cfg_encoding = enc

    #--------------------------------------------------------------------------
    def init_cfgfiles(self):
        """Method to generate the self.cfg_files list."""

        self.cfg_files = []

        # add /etc/app/app.cfg or $VIRTUAL_ENV/etc/app/app.cfg
        etc_dir = os.sep + 'etc'
        if os.environ.has_key('VIRTUAL_ENV'):
            etc_dir = os.path.join(os.environ['VIRTUAL_ENV'], 'etc')
        syscfg_fn = os.path.join(etc_dir, self.appname, '%s.cfg' % self.appname)
        self.cfg_files.append(syscfg_fn)

        # add $HOME/.app/app.cfg
        home_dir = None
        if os.environ.has_key('HOME'):
            home_dir = os.environ['HOME']
            if self.verbose > 1:
                log.debug("home_dir: %s", home_dir)
            usercfg_fn = os.path.join(home_dir, (".%s" % (self.appname)),
                    (self.appname + '.cfg'))
            self.cfg_files.append(usercfg_fn)

        # add a configfile given on command line with --cfg-file
        cmdline_cfg = getattr(self.args, 'cfg_file', None)
        if cmdline_cfg:
            self.cfg_files.append(cmdline_cfg)

    #--------------------------------------------------------------------------
    def _init_cfg_spec(self):
        """
        Initialize self.cfg_spec with the content of a config specification
        file (See: http://www.voidspace.org.uk/python/configobj.html#validation)

        The content of self.cfg_spec will be used on reading the configuration
        for the validation of their content.

        """

        self.cfg_spec = ''

        self.init_cfg_spec()

        self.cfg_spec = "\n" + dedent("""\
        [general]
        verbose = integer(0, 10, default = 0)
        """) + self.cfg_spec

    #--------------------------------------------------------------------------
    def init_cfg_spec(self):
        """
        Dummy method to complete the initialisation of the config
        specification file.

        It will called before reading the configuration files and
        their validation.

        This method can be overriden in descsendant classes.

        """

        pass

    #--------------------------------------------------------------------------
    def _read_config(self):
        """
        Read in configuration from all configuration files
        stored in self.cfg_files in the order, how they are stored there.

        The found configuration is merged into self.cfg.

        NOTE: all generated keys and string values are decoded to unicode.

        """

        if self.verbose > 2:
            log.debug("Read cfg files with character set '%s' ...",
                    self.cfg_encoding)

        configspec = ConfigObj(
                StringIO(self.cfg_spec),
                encoding = self.cfg_encoding,
                list_values = False,
                _inspec = True
        )
        if self.verbose > 2:
            log.debug("Used config specification:\n%s", pp(configspec))
        validator = Validator()

        cfgfiles_ok = True

        for cfg_file in self.cfg_files:

            if self.verbose > 1:
                log.debug("Reading in configuration file '%s' ...", cfg_file)

            cfg = ConfigObj(
                    cfg_file,
                    encoding = self.cfg_encoding,
                    stringify = True,
                    configspec = configspec,
            )

            if self.verbose > 2:
                log.debug("Found configuration:\n%r", pp(cfg))

            result = cfg.validate(validator, preserve_errors = True)
            if self.verbose > 2:
                log.debug("Validation result:\n%s", pp(result))

            if not result is True:
                cfgfiles_ok = False
                msg = _("Wrong configuration in '%s' found:") % (cfg_file)
                msg += '\n' + self._transform_cfg_errors(result)
                self.handle_error(msg, _("Configuration error"))
                continue

            self.cfg.rec_update(cfg)

        if not cfgfiles_ok:
            sys.exit(2)

        if self.verbose > 2:
            log.debug("Merged configuration:\n%r", pp(self.cfg))

    #--------------------------------------------------------------------------
    def _transform_cfg_errors(self, result, div = None):
        """
        Transforms a validation result of the form::
            {u'general': {u'verbose': VdtValueTooSmallError('the value "-1" is too small.',)}}

        to a string in the form::
            In section [general] key 'verbose': the value "-1" is too small.

        Every found error in this result is placed a new line at the
        end of this string.

        @return: a textual representation of the configuration errors (multilined)
        @rtype: str

        """

        if result is None:
            return "Undefined error"

        error_str = ''
        for key in result:
            val = result[key]
            if isinstance(val, dict):
                ndiv = []
                if div:
                    for a in div:
                        ndiv.append(a)
                ndiv.append(key)
                part_err_str = self._transform_cfg_errors(val, ndiv)
                error_str += part_err_str
            else:
                section = '-'
                if div:
                    section = ', '.join(map(
                            lambda x: ('[' + x.encode('utf8') + ']'), div))
                msg = (_("In section %s key '%s': %s") + "\n") % (
                        section, key.encode('utf8'), str(val).encode('utf8'))
                error_str += msg

        return error_str

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
