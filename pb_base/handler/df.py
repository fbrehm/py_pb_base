#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: A special handler module for a handling the df-command and his results.
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

__version__ = '0.2.1'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

# Some module varriables
DF_CMD = os.sep + os.path.join('bin', 'df')

#==============================================================================
class DfError(PbBaseHandlerError):
    """
    Special exception class on executing the df command.
    """

    pass

#==============================================================================
class DfResult(PbBaseObject):

    #--------------------------------------------------------------------------
    def __init__(self,
            dev = None,
            fs_type = None,
            total = 0l,
            used = 0l,
            free = 0l,
            fs = None,
            appname = None,
            verbose = 0,
            base_dir = None
            ):
        """
        Initialisation of the DfResult object.

        @param dev: the appropriate device of the filesystem from 'df'
        @type dev: str
        @param fs_type: the type of the filesystem (e.g. 'ext3', 'nfs' a.s.o.)
        @type fs_type: str
        @param total: the total size of the filesystem in Bytes
        @type total: long
        @param used: the used area of the filesystem in Bytes
        @type used: long
        @param free: the free space of the filesystem in Bytes
        @type free: long
        @param fs: the name of the filesystem
        @type fs: str

        """

        super(DfResult, self).__init__(
                appname = appname,
                verbose = verbose,
                base_dir = base_dir,
                initialized = False
        )

        self._dev = str(dev)
        """
        @ivar: appropriate device of the filesystem from 'df'
        @type: str
        """

        self._fs_type = fs_type
        """
        @ivar: the type of the filesystem (e.g. 'ext3', 'nfs' a.s.o.)
        @type: str
        """

        self._total = long(total)
        """
        @ivar: the total size of the filesystem in Bytes
        @type: long
        """

        self._used = long(used)
        """
        @ivar: the used area of the filesystem in Bytes
        @type: long
        """

        self._free = long(free)
        """
        @ivar: the free space of the filesystem in Bytes
        @type: long
        """

        self._fs = str(fs)
        """
        @ivar: the name of the filesystem
        @type: str
        """

        self.initialized = True

    #------------------------------------------------------------
    @property
    def dev(self):
        """The appropriate device of the filesystem from 'df'"""
        return self._dev

    #------------------------------------------------------------
    @property
    def fs_type(self):
        """The type of the filesystem (e.g. 'ext3', 'nfs' a.s.o.)"""
        return self._fs_type

    #------------------------------------------------------------
    @property
    def total(self):
        """The total size of the filesystem in Bytes."""
        return self._total

    #------------------------------------------------------------
    @property
    def total_kb(self):
        """The total size of the filesystem in KiBytes."""
        return self._total / 1024l

    #------------------------------------------------------------
    @property
    def total_mb(self):
        """The total size of the filesystem in MiBytes."""
        return int(self._total / 1024l / 1024l)

    #------------------------------------------------------------
    @property
    def used(self):
        """The used area of the filesystem in Bytes."""
        return self._used

    #------------------------------------------------------------
    @property
    def used_kb(self):
        """The used area of the filesystem in KiBytes."""
        return self._used / 1024l

    #------------------------------------------------------------
    @property
    def used_mb(self):
        """The used area of the filesystem in MiBytes."""
        return int(self._used / 1024l / 1024l)

    #------------------------------------------------------------
    @property
    def free(self):
        """The free space of the filesystem in Bytes."""
        return self._free

    #------------------------------------------------------------
    @property
    def free_kb(self):
        """The free space of the filesystem in KiBytes."""
        return self._free / 1024l

    #------------------------------------------------------------
    @property
    def free_mb(self):
        """The free space of the filesystem in MiBytes."""
        return int(self._free / 1024l / 1024l)

    #------------------------------------------------------------
    @property
    def fs(self):
        """The name of the filesystem."""
        return self._fs

    #------------------------------------------------------------
    @property
    def used_percent(self):
        """The percentual value of used space on filesystem."""
        if not self.total:
            return None
        return float(self.used) / float(self.total) * 100.0

    #------------------------------------------------------------
    @property
    def free_percent(self):
        """The percentual value of free space on filesystem."""
        if not self.total:
            return None
        return float(self.free) / float(self.total) * 100.0

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(DfResult, self).as_dict()
        res['dev'] = self.dev
        res['fs'] = self.fs
        res['fs_type'] = self.fs_type
        res['total'] = self.total
        res['total_kb'] = self.total_kb
        res['total_mb'] = self.total_mb
        res['used'] = self.used
        res['used_kb'] = self.used_kb
        res['used_mb'] = self.used_mb
        res['used_percent'] = self.used_percent
        res['free'] = self.free
        res['free_kb'] = self.free_kb
        res['free_mb'] = self.free_mb
        res['free_percent'] = self.free_percent

        return res

#==============================================================================
class DfHandler(PbBaseHandler):
    """
    A special handler class to retrieve informations about space of filesystems.

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
        The execution of executing 'df' should never been simulated.

        @raise CommandNotFoundError: if the 'df' command could not be found.
        @raise DfError: on a uncoverable error.

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

        super(DfHandler, self).__init__(
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

        self._df_cmd = DF_CMD
        """
        @ivar: the underlaying 'df' command
        @type: str
        """
        if not os.path.exists(self.df_cmd) or not os.access(
                self.df_cmd, os.X_OK):
            self._df_cmd = self.get_command('df')
        if not self.df_cmd:
            failed_commands.append('df')

        self.re_df_line = re.compile(
                r'(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s*%\s+(.*)')

        # Some commands are missing
        if failed_commands:
            raise CommandNotFoundError(failed_commands)

        self.initialized = True
        if self.verbose > 3:
            log.debug(_("Initialized."))

    #------------------------------------------------------------
    @property
    def df_cmd(self):
        """The absolute path to the OS command 'df'."""
        return self._df_cmd

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Transforms the elements of the object into a dict

        @return: structure as dict
        @rtype:  dict
        """

        res = super(DfHandler, self).as_dict()
        res['df_cmd'] = self.df_cmd

        return res

    #--------------------------------------------------------------------------
    def __call__(self, fs = None, all_fs = False, local = False, sync = False,
            fs_type = None, exclude_type = None):
        """
        Executes the df command and returns a list of all found filesystems.

        Through the special name __call__() it's possible, the instance variable
        of this class to use as a funktion. So there can be executet simple
        df requests:

            df = DfHandler()

            df_list = df()
            df_list = df('/tmp')
            df_list = df(['/', '/var'])

            ...

        @param fs: the filesystem or filesystems, from where to get informations.
                   if omitted, all filesystems are checked
        @type fs: None, str or list of str
        @param all_fs: include dummy file systems, ignored, if dedicated filesystems
                       are given with parameter fs
        @type all_fs: bool
        @param local: limit listing to local file systems, ignored, if dedicated
                      filesystems are given with parameter fs
        @type local: bool
        @param sync: invoke sync before getting usage info
        @type sync: bool
        @param fs_type: limit listing to file systems ofgiven types, ignored, if
                        dedicated filesystems are given with parameter fs
        @type fs_type: None or list of str
        @param exclude_type: limit listing to file systems not ofgiven types,
                             ignored, if dedicated filesystems are given with
                             parameter fs
        @type exclude_type: None or list of str

        @return: informations about all requested filesystems
        @rtype: list of DfResult

        """

        if fs:
            if isinstance(fs, basestring):
                fs = [fs]
        else:
            fs = []

        for fs_object in fs:
            if self.verbose > 2:
                log.debug(_("Checking existence of %r ..."), fs_object)
            if not os.path.exists(fs_object):
                raise DfError(_("Filesystem object %r doesn't exists.") %
                        (fs_object))

            if not os.path.isabs(fs_object):
                raise DfError(_("%r is not given as an absolute path.") %
                        (fs_object))

        if self.verbose > 1:
            if fs:
                msg = (_("Calling 'df' for the following objects:") +
                        "\n%r") % (fs)
            else:
                if all_fs:
                    msg = _("Calling 'df' for real all filesystems.")
                elif local:
                    msg = _("Calling 'df' for local filesystems.")
                else:
                    msg = _("Calling 'df' for all filesystems.")
            log.debug(msg)

        cmd = [self.df_cmd, '-k', '-P', '--print-type']
        if all_fs:
            cmd.append('--all')
        elif local:
            cmd.append('--local')
        if sync:
            cmd.append('--sync')

        if fs_type:
            param = '--type=%s'
            if isinstance(fs_type, basestring):
                cmd.append(param % (fs_type))
            else:
                for fstype in fs_type:
                    cmd.append(param % (fstype))

        if exclude_type:
            param = '--exclude-type=%s'
            if isinstance(exclude_type, basestring):
                cmd.append(param % (exclude_type))
            else:
                for ex_type in exclude_type:
                    cmd.append(param % (ex_type))

        for fs_object in fs:
            cmd.append(fs_object)

        cmdline = ' '.join(cmd)
        (ret_code, std_out, std_err) = self.call(cmd)

        if ret_code:
            err = _('Undefined error')
            if std_err:
                e = std_err.replace('\n', ' ').strip()
                if e:
                    err = e
            msg = _("Error %(nr)d on getting free space of %(obj)r: %(err)s") % {
                    ret_code, fs, err}
            raise DfError(msg)

        lines = std_out.splitlines()
        if not lines or len(lines) < 2:
            msg = (_("Didn't found any usable information in output of %r:") +
                    " %r") % ( cmdline, std_out)
            raise DfError(msg)

        del lines[0]
        df_list = []

        for line in lines:

            line = line.strip()
            match = self.re_df_line.search(line)
            if not match:
                msg = _("Could not evaluate line %(line)r in output of command %(cmd)r.") % {
                        'line': line, 'cmd': cmdline}
                raise DfError(msg)

            df_result = DfResult(
                    dev = match.group(1),
                    fs_type = match.group(2),
                    total = long(match.group(3)) * 1024l,
                    used = long(match.group(4)) * 1024l,
                    free = long(match.group(5)) * 1024l,
                    fs =  match.group(6),
                    appname = self.appname,
                    verbose = self.verbose,
                    base_dir = self.base_dir,
            )
            df_list.append(df_result)

        return df_list

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
