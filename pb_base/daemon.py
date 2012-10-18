#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a base daemon application object.
          It provides all from the configured application object with
          additional methods and properties to daemonize itself.
"""

# Standard modules
import sys
import os
import logging
import datetime

from gettext import gettext as _

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError

from pb_base.cfg_app import PbCfgAppError
from pb_base.cfg_app import PbCfgApp

__version__ = '0.0.1'

log = logging.getLogger(__name__)

#==============================================================================
class PbDaemonError(PbCfgAppError):
    """Base error class for all exceptions happened during
    execution this daemon application"""

    pass

#==============================================================================
class PbDaemon(PbCfgApp):
    """
    Base class for all daemon application objects.
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
                ):
        """
        Initialisation of the daemon object.

        @raise PbDaemonError: on a uncoverable error.

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

        @return: None
        """

        super(PbDaemon, self).__init__(
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
        )


    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.

        This method should be explicitely called by all init_arg_parser()
        methods in descendant classes.
        """

        self.arg_parser.add_argument(
                '-f', "--foreground",
                action = 'store_true',
                dest = "foreground",
                default = False,
                help = _('Let the process run in foreground and not as a daemon.'),
        )

        super(PbDaemon, self).init_arg_parser()


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
