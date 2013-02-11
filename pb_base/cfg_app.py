#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for a base configured application object.
          It provides all from the base application object with additional
          methods and properties to read different configuration files.
"""

# Standard modules
import sys
import os
import logging
import datetime

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

from pb_base.validator import pbvalidator_checks

from pb_base.app import PbApplicationError
from pb_base.app import PbApplication

from pb_base.translate import translator

__version__ = '0.5.5'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

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
                cfg_dir = None,
                cfg_stem = None,
                cfg_encoding = 'utf8',
                cfg_spec = None,
                hide_default_config = False,
                need_config_file = False,
                ):
        """
        Initialisation of the base object.

        @raise PbCfgAppError: on a uncoverable error.

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
        @param cfg_spec: Specification for configfile
        @type cfg_spec: str
        @param hide_default_config: hide command line parameter --default-config and
                                    don't execute generation of default config
        @type hide_default_config: bool
        @param need_config_file: through an error message, if none of the default
                                 configuration files were found
        @type need_config_file: bool

        @return: None
        """

        self._cfg_encoding = cfg_encoding
        """
        @ivar: encoding character set of the configuration files
        @type: str
        """

        self._hide_default_config = bool(hide_default_config)
        """
        @ivar: hide command line parameter --default-config and
               don't execute generation of default config
        @type: bool
        """

        self._need_config_file = bool(need_config_file)
        """
        @ivar: through an error message, if none of the default configuration files were found
        @type: bool
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

        self._cfg_dir = None
        """
        @ivar: Directory name under /etc or $HOME respectively, where the the
               normal configuration file should be located.
               For looking under $HOME, a leading '.' on this directory name
               is assumed.
        @type: str
        """
        if cfg_dir is None:
            self._cfg_dir = self.appname
        else:
            d = str(cfg_dir).strip()
            if d == '':
                self._cfg_dir = None
            else:
                self._cfg_dir = d

        self._cfg_stem = None
        """
        @ivar: the basename of the configuration file without any file extension
        @type: str
        """
        if cfg_stem:
            s = str(cfg_stem).strip()
            if not s:
                msg = "Invalid configuration stem %r given." % (cfg_stem)
                raise PbCfgAppError(msg)
            self._cfg_stem = s
        else:
            self._cfg_stem = self.appname

        self.cfg_files = []
        """
        @ivar: all configuration files to use for this application in the order
               of reading in them - the file with the lowest priority first,
               this file with the highest priority at last.
        @type: list of str
        """
        self.init_cfgfiles()

        self.cfg_spec = None
        """
        @ivar: a specification of the configuration, which should
               be found in the configuration files.
               See: http://www.voidspace.org.uk/python/configobj.html#validation
               how to write such a specification.
        @type: str
        """
        if cfg_spec:
            if type(cfg_spec) is str:
                self.cfg_spec = ConfigObj(cfg_spec.split('\n'))
            elif type(cfg_spec) is ConfigObj:
                self.cfg_spec = cfg_spec
        else:
            self.cfg_spec = ConfigObj()
            self._init_cfg_spec()

        enc = getattr(self.args, 'cfg_encoding', None)
        if enc:
            enc = enc.lower()
            if enc != self.cfg_encoding:
                self._cfg_encoding = enc

        self._read_config()

    #------------------------------------------------------------
    @property
    def need_config_file(self):
        """
        hide command line parameter --default-config and
        don't execute generation of default config
        """
        return getattr(self, '_need_config_file', False)

    #------------------------------------------------------------
    @property
    def hide_default_config(self):
        """
        Through an error message, if none of the default configuration files
        were found.
        """
        return getattr(self, '_hide_default_config', False)

    #------------------------------------------------------------
    @property
    def cfg_encoding(self):
        """The encoding character set of the configuration files."""
        return self._cfg_encoding

    #------------------------------------------------------------
    @property
    def cfg_dir(self):
        """The directory containing the configuration files."""
        return self._cfg_dir

    #------------------------------------------------------------
    @property
    def cfg_stem(self):
        """The basename of the configuration file without any file extension."""
        return self._cfg_stem

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(PbCfgApp, self).as_dict(short = short)
        res['need_config_file'] = self.need_config_file
        res['hide_default_config'] = self.hide_default_config
        res['cfg_encoding'] = self.cfg_encoding
        res['cfg_dir'] = self.cfg_dir
        res['cfg_stem'] = self.cfg_stem

        return res

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

        if not self.hide_default_config:
            self.arg_parser.add_argument(
                    "--default-config",
                    action = 'store_true',
                    dest = "show_default_config",
                    help = _('Generates a default configuration, prints ' +
                            'it out to STDOUT and exit'),
            )

    #--------------------------------------------------------------------------
    def init_cfgfiles(self):
        """Method to generate the self.cfg_files list."""

        self.cfg_files = []

        # add /etc/app/app.cfg or $VIRTUAL_ENV/etc/app/app.cfg
        etc_dir = os.sep + 'etc'
        if os.environ.has_key('VIRTUAL_ENV'):
            etc_dir = os.path.join(os.environ['VIRTUAL_ENV'], 'etc')
        syscfg_fn = None
        if self.cfg_dir:
            syscfg_fn = os.path.join(etc_dir, self.cfg_dir, '%s.cfg' % (self.cfg_stem))
        else:
            syscfg_fn = os.path.join(etc_dir, '%s.cfg' % (self.cfg_stem))
        self.cfg_files.append(syscfg_fn)

        # add $HOME/.app/app.cfg
        home_dir = None
        if os.environ.has_key('HOME'):
            home_dir = os.environ['HOME']
            if self.verbose > 1:
                log.debug("home_dir: %s", home_dir)
            usercfg_fn = None
            if self.cfg_dir:
                usercfg_fn = os.path.join(home_dir, (".%s" % (self.cfg_dir)),
                        ('%s.cfg' % (self.cfg_stem)))
            else:
                usercfg_fn = os.path.join(home_dir,
                        (".%s.cfg" % (self.cfg_stem)))
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

        self.cfg_spec.initial_comment.append(u'Configuration of %s' % (self.appname))
        self.cfg_spec.initial_comment.append('')

        self.init_cfg_spec()

        if not u'general' in self.cfg_spec:
            self.cfg_spec[u'general'] = {}

        self.cfg_spec.comments[u'general'].append('')
        self.cfg_spec.comments[u'general'].append(
                u'General configuration parameters')

        if not u'verbose' in self.cfg_spec[u'general']:
            self.cfg_spec[u'general'][u'verbose'] = 'integer(0, 10, default = 0)'
            self.cfg_spec[u'general'].comments[u'verbose'].append('')
            self.cfg_spec[u'general'].comments[u'verbose'].append(
                    u'Defines a minimum verbosity of the application')

        self.cfg_spec.final_comment.append('')
        self.cfg_spec.final_comment.append('')
        self.cfg_spec.final_comment.append(
                u'vim: filetype=cfg fileencoding=utf-8 ts=4 expandtab')

    #--------------------------------------------------------------------------
    def init_cfg_spec(self):
        """
        Dummy method to complete the initialisation of the config
        specification file.

        It will called before reading the configuration files and
        their validation.

        This method can be overriden in descendant classes.

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
            log.debug(_("Read cfg files with character set '%s' ..."),
                    self.cfg_encoding)

        if self.verbose > 3:
            cfgspec = StringIO()
            self.cfg_spec.write(cfgspec)
            log.debug((_("Used config specification:") + "\n%s"),
                    cfgspec.getvalue())
            cfgspec.close()
            del cfgspec

        validator = Validator(pbvalidator_checks)

        cfgfiles_ok = True

        existing_cfg_files = [file for file in self.cfg_files
                              if os.path.isfile(file)]

        if not existing_cfg_files and self.need_config_file:
            msg = "Could not find any configuration file at these locations:"
            for file in self.cfg_files:
                msg += '\n' + file
            sys.exit(msg)

        for cfg_file in existing_cfg_files:

            if self.verbose > 1:
                log.debug(_("Reading in configuration file '%s' ..."),
                          cfg_file)

            cfg = ConfigObj(
                    cfg_file,
                    encoding = self.cfg_encoding,
                    stringify = True,
                    configspec = self.cfg_spec,
            )

            if self.verbose > 2:
                log.debug((_("Found configuration:") + "\n%r"), pp(cfg))

            result = cfg.validate(
                    validator, preserve_errors = True, copy = True)
            if self.verbose > 2:
                log.debug((_("Validation result:") + "\n%s"), pp(result))

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
            if len(existing_cfg_files) > 1:
                log.debug((_("Using merged configuration:") + "\n%r"),
                        pp(self.cfg))
            else:
                log.debug((_("Using configuration:") + "\n%r"), pp(self.cfg))

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
            return _("Undefined error")

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
                if val is True:
                    continue
                if val is False:
                    val = "missing"
                section = '-'
                if div:
                    section = ', '.join(map(
                            lambda x: ('[' + x.encode('utf8') + ']'), div))
                msg = (_("In section %(section)s key '%(key)s': %(value)s") +
                        "\n") % {'section': section, 'key': key.encode('utf8'),
                        'value': str(val).encode('utf8')}
                error_str += msg

        return error_str

    #--------------------------------------------------------------------------
    def perform_config(self):
        """
        Execute some actions after reading the configuration.

        This method should be explicitely called by all perform_config()
        methods in descendant classes.
        """

        if (u'general' in self.cfg and
                u'verbose' in self.cfg[u'general']):

            new_verbose = self.cfg[u'general'][u'verbose']
            if new_verbose > self.verbose:
                self.verbose = new_verbose

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

        self.perform_config()
        self.perform_arg_parser()
        self.init_logging()

        self.initialized = True

    #--------------------------------------------------------------------------
    def pre_run(self):
        """
        Code executing before executing the main routine.

        This method should be explicitely called by all pre_run()
        methods in descendant classes.

        If the command line parameter '--default-config' was given, the defined
        default configuration is printed out to stdout and the application
        exit with a return value of 0.

        """

        if self.hide_default_config:
            return

        if not self.args.show_default_config:
            return

        curdate = datetime.datetime.utcnow()

        self.cfg_spec.initial_comment.append('')
        self.cfg_spec.initial_comment.append(
                (u'Generated at: %s UTC' % (curdate.isoformat(' '))))
        self.cfg_spec.initial_comment.append('')

        cfg = ConfigObj(
                infile = None,
                encoding = self.cfg_encoding,
                stringify = True,
                configspec = self.cfg_spec,
        )

        vdt = Validator(pbvalidator_checks)
        cfg.validate(vdt, copy = True)
        cfg.write(sys.stdout)

        sys.exit(0)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
