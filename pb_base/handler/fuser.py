#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: A special handler module for a handling the fuser command
"""

# Standard modules
import sys
import os
import logging
import re

# Own modules
from pb_base.common import pp

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

import pb_base.handler
from pb_base.handler import PbBaseHandlerError
from pb_base.handler import CommandNotFoundError
from pb_base.handler import PbBaseHandler

from pb_base.translate import translator

__version__ = '0.1.1'

log = logging.getLogger(__name__)

# Some module varriables
FUSER_CMD = os.sep + os.path.join('bin', 'fuser')

_ = translator.lgettext
__ = translator.lngettext

#==============================================================================
class FuserError(PbBaseHandlerError):
    """
    Special exception class on executing the fuser command.
    """

    pass

#==============================================================================
class FuserHandler(PbBaseHandler):
    """
    A special handler class to retrieve informations about processes opening
    a file or mountpoint

    An instance of this class may be used as a function, see method __call__().

    """

    #--------------------------------------------------------------------------
    def __init__(self,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            initialized = False,
            sudo = False,
            quiet = False,
            ):
        """
        Initialisation of the df handler object.
        The execution of executing 'fuser' should never been simulated.

        @raise CommandNotFoundError: if the 'fuser' command could not be found.
        @raise FuserError: on a uncoverable error.

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
        @param sudo: should the command executed by sudo by default
        @type sudo: bool
        @param quiet: don't display ouput of action after calling
        @type quiet: bool

        @return: None
        """

        super(FuserHandler, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
                simulate = False,
                sudo = sudo,
                quiet = quiet,
        )
        self.initialized = False

        failed_commands = []

        self._fuser_cmd = FUSER_CMD
        """
        @ivar: the underlaying 'fuser' command
        @type: str
        """
        if not os.path.exists(self.fuser_cmd) or not os.access(
                self.fuser_cmd, os.X_OK):
            self._fuser_cmd = self.get_command('fuser')
        if not self.fuser_cmd:
            failed_commands.append('fuser')

        # Some commands are missing
        if failed_commands:
            raise CommandNotFoundError(failed_commands)

        self.initialized = True
        if self.verbose > 3:
            log.debug(_("Initialized."))

    #------------------------------------------------------------
    @property
    def fuser_cmd(self):
        """The absolute path to the OS command 'fuser'."""
        return self._fuser_cmd

    #--------------------------------------------------------------------------
    def __call__(self, fs_object, force = False):
        """
        Executes the fuser command and returns a list of all process IDs using
        this filesystem object.

        @raise FuserError: if the given filesystem object doesn't exists or on
                           other errors.

        @param fs_object: the filesystem object to check, must exists
        @type fs_object: str
        @param force: execute fuser, even that the given filesystem object
                      doesn't seems to exists
        @type force: bool

        @return: list of all process IDs using this filesystem object. An empty
                 list, if no process is using this object.
        @rtype: list of int

        """

        if not os.path.exists(fs_object):
            if force:
                log.warn(_("Filesystem object %r doesn't seems to exist. Continue because of the 'force' flag."), fs_object)
            else:
                msg = _("Filesystem object %r doesn't seems to exist.") % (
                        fs_object)
                raise FuserError(msg)

        do_sudo = False
        if os.geteuid():
            do_sudo = True

        cmd = [self.fuser_cmd, fs_object]
        cmdline = ' '.join(cmd)
        (ret_code, std_out, std_err) = self.call(cmd, sudo = do_sudo)

        if ret_code:

            if ret_code == 1:

                if self.verbose > 1:
                    log.debug(_("%r will not be used by some other processes."),
                            fs_object)
                return []

            err = _('Undefined error')
            if std_err:
                e = std_err.replace('\n', ' ').strip()
                if e:
                    err = e
            msg = _("Error %(nr)d on getting fuser information of %(obj)r: %(err)s") % {
                    'nr': ret_code, 'obj': fs_object, 'err': err}
            raise FuserError(msg)

        pid_list = []
        lines = std_out.splitlines()
        line = lines[0].strip()
        if line:
            pids = line.split()
            for pid in pids:
                pid_int = None
                try:
                    pid_int = int(pid)
                except ValueError, e:
                    log.warn(_("%r is not an integer value usable as PID."), pid)
                    continue
                pid_list.append(pid_int)

        return pid_list

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
