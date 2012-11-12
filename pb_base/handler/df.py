#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: A special handler module for a handling the df-command and hist results.
"""

# Standard modules
import sys
import os
import logging
import re

from gettext import gettext as _

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

__version__ = '0.1.0'

log = logging.getLogger(__name__)

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

    #------------------------------------------------------------
    @property
    def dev(self):
        """The appropriate device of the filesystem from 'df'"""
        return self._dev

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
        res['total_mb'] = self.total_mb
        res['used_mb'] = self.used_mb
        res['free_mb'] = self.free_mb
        res['used_percent'] = self.used_percent
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
        The execution of executing 'df' shouldnever been simulated.

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

        # Some commands are missing
        if failed_commands:
            raise CommandNotFoundError(failed_commands)

        self.initialized = True
        if self.verbose > 3:
            log.debug("Initialized.")

    #------------------------------------------------------------
    @property
    def df_cmd(self):
        """The absolute path to the OS command 'df'."""
        return self._df_cmd

    #--------------------------------------------------------------------------
    def __call__(self, fs = None, all_fs = False, local = False, sync = False,
            fs_type = None, exclude_type = None):
        """
        Executes the df command and returns a list of all found filesystems.

        """

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
