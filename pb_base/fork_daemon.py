#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for a daemon application object, which is forking
          to execute the underlaying action.
          It provides all from the daemon application object with
          additional methods and properties for forking.
"""

# Standard modules
import sys
import os
import logging
import time
import signal

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

from pb_base.daemon import PbDaemonError
from pb_base.daemon import PbDaemon

from pb_base.translate import translator

__version__ = '0.2.0'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext
if sys.version_info[0] > 2:
    _ = translator.gettext
    __ = translator.ngettext

#--------------------------------------------------------------------------

default_max_children = 10
maximum_max_children = 4096
default_timeout_collect_children = 10

#==============================================================================
class ForkingDaemonError(PbDaemonError):
    """Base error class for all exceptions happened during
    execution this daemon application"""

    pass

#==============================================================================
class ForkingDaemon(PbDaemon):
    """
    Base class for a forking daemon application objects.
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
                max_children = default_max_children,
                ):
        """
        Initialisation of the daemon object.

        @raise ForkingDaemonError: on a uncoverable error.

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
        @param max_children: the maximum number of forked children,
                             that may be exists on a particular moment
        @type max_children: int

        @return: None
        """

        self._is_child = False
        """
        @ivar: Flag, whether the current process is a child handling process
        @type: bool
        """

        self._max_children = max_children
        """
        @ivar: maximum number of child processes
        @type: int
        """

        self.active_children = {}
        """
        @ivar: all active children processes with their PID
               as keys and their child ID as value (for the parent process)
        @type: dict
        """

        self.child_ids = {}
        """
        @ivar: the opposite of self.active_children - child ID's are the keys
               and the PIDs are the values
        @type: dict
        """

        self._child_id = 0
        """
        @ivar: the ID of the current child process, if it is a child
               if Zero, it's the parent process
        @type: int
        """

        self._timeout_collect_children = default_timeout_collect_children
        """
        @ivar: maximum timeout on collecting finished children per stage
               if there are too many child processes on every stage
               an increased level of signal is sent to all child processes
               (None -> SIGHUP -> SIGTERM -> SIGKILL)
        @type: int
        """

        super(ForkingDaemon, self).__init__(
                appname = appname,
                do_daemonize = do_daemonize,
                pidfile = pidfile,
                error_log = error_log,
                facility = facility,
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

    #------------------------------------------------------------
    @property
    def is_child(self):
        """Flag, whether the current process is a child handling process."""
        return self._is_child

    #------------------------------------------------------------
    @property
    def max_children(self):
        """The maximum number of child processes."""
        return self._max_children

    @max_children.setter
    def max_children(self, value):
        v = int(value)
        if v < 1 or v > maximum_max_children:
            msg = _("Wrong value for max_children %(val)d, must be between 1 and %(max)d.") % {
                    'val': v, 'max': maximum_max_children}
            raise ValueError(msg)
        self._max_children = v

    #------------------------------------------------------------
    @property
    def child_id(self):
        """The ID of the current child process."""
        return self._child_id

    #------------------------------------------------------------
    @property
    def timeout_collect_children(self):
        """The maximum timeout on collecting finished children per stage"""
        return self._timeout_collect_children

    @timeout_collect_children.setter
    def timeout_collect_children(self, value):
        v = int(value)
        if v < 1:
            msg = _("Wrong value for timeout_collect_children %d, must be greater than zero.") % (v)
            raise ValueError(msg)
        self._timeout_collect_children = v

    #--------------------------------------------------------------------------
    def as_dict(self, short = False):
        """
        Transforms the elements of the object into a dict

        @param short: don't include local properties in resulting dict.
        @type short: bool

        @return: structure as dict
        @rtype:  dict
        """

        res = super(ForkingDaemon, self).as_dict(short = short)
        res['is_child'] = self.is_child
        res['max_children'] = self.max_children
        res['child_id'] = self.child_id
        res['timeout_collect_children'] = self.timeout_collect_children

        return res

    #--------------------------------------------------------------------------
    def init_cfg_spec(self):
        """
        Method to complete the initialisation of the config
        specification file.

        It will called before reading the configuration files and
        their validation.

        """

        super(ForkingDaemon, self).init_cfg_spec()

        if not 'general' in self.cfg_spec:
            self.cfg_spec['general'] = {}

        max_spec = 'integer(min = 1, max = %d, default = %d)' % (
                maximum_max_children, self._max_children)

        if not 'max_children' in self.cfg_spec['general']:
            self.cfg_spec['general']['max_children'] = max_spec
            self.cfg_spec['general'].comments['max_children'].append('')
            self.cfg_spec['general'].comments['max_children'].append(
                    'The maximum number of child processes.')

        to_spec = 'integer(min = 1, default = %d)' % (
                default_timeout_collect_children)

        if not 'timeout_collect_children' in self.cfg_spec['general']:
            self.cfg_spec['general']['timeout_collect_children'] = to_spec
            self.cfg_spec['general'].comments['timeout_collect_children'].append('')
            self.cfg_spec['general'].comments['timeout_collect_children'].append(
                    'The maximum timeout on collecting finished children per stage.')

    #--------------------------------------------------------------------------
    def perform_config(self):
        """
        Execute some actions after reading the configuration.

        This method should be explicitely called by all perform_config()
        methods in descendant classes.
        """

        super(ForkingDaemon, self).perform_config()

        if 'general' in self.cfg and 'max_children' in self.cfg['general']:
            self.max_children = self.cfg['general']['max_children']

        if ('general' in self.cfg and
                'timeout_collect_children' in self.cfg['general']):
            self.timeout_collect_children = self.cfg['general']['timeout_collect_children']

    #--------------------------------------------------------------------------
    def post_run(self):
        """Code executing after executing the main routine."""

        if self.verbose > 1:
            log.info(_("Cleaning up ..."))

        # Collect all children processes
        self.collect_children(collect_all = True)
        self.pidfile = None

        if self.initialized or self.verbose > 1:
            log.info(_("Ending."))

        if self.is_daemon:
            self.handle_info(_("Daemon (v%s) ended.") % (self.version),
                    self.appname)

    #--------------------------------------------------------------------------
    def handle_timeout(self):
        '''
        Wait for zombies after an unsuccessful polling intervall and
        doing some stuff in a waiting loop.
        '''

        self.collect_children()

    #--------------------------------------------------------------------------
    def collect_children(self, collect_all = False):
        """
        Internal routine to wait for children that have exited.

        If all children should collected, then it depends on
        self.forced_shutdown, whether running childs should be killed or not.

        @param collect_all: flag to collect all active children, instead
                            of to let a number of children
        @type collect_all:  bool
        """

        if collect_all:
            if self.verbose > 2:
                log.debug(_("Collecting all child processes ..."))
        else:
            if self.verbose > 5:
                log.debug(_("Collecting finished child processes ..."))

        if len(self.active_children) < 1:
            if self.verbose > 5:
                log.debug(_("No active children found."))
            return

        maximum = self.max_children
        if collect_all:
            maximum = 0

        begin = time.time()
        polling_time = 0.05
        if self.verbose > 1:
            polling_time = 1

        timeout = self.timeout_collect_children
        stage = 1

        while len(self.active_children) > maximum:

            do_kill = False
            if collect_all and self.forced_shutdown:
                do_kill = True

            cur_time = time.time() - begin

            if do_kill and (cur_time >= timeout):

                # Sending kill to child processes
                the_signal = signal.SIGHUP
                if stage == 2:
                    the_signal = signal.SIGTERM
                elif stage == 3:
                    the_signal = signal.SIGKILL

                log.info(_("Sending signal %d to all child processes."),
                        the_signal)
                for pid in list(self.active_children.keys()):
                    try:
                        os.kill(pid, the_signal)
                    except:
                        pass

                stage += 1
                if stage > 3:
                    msg = _("Maximum timeout of %d seconds for waiting on finished child processes reached.")
                    log.error(msg, (timeout * 3))
                    raise ForkingDaemonError(msg)
                begin = time.time()
                log.debug(_("New stage %d in waiting for child processes."), stage)

            if self.verbose > 1:
                log.debug(_("Waiting for finished children, stage %d."), stage)

            # XXX: This will wait for any child process, not just ones
            # spawned by this library. This could confuse other
            # libraries that expect to be able to wait for their own
            # children.
            try:
                pid, status = os.waitpid(0, os.WNOHANG)
            except os.error:
                pid = None
            if pid:
                if pid in self.active_children:
                    self._deregister_child(pid)
                continue

            time.sleep(polling_time)

        if len(self.active_children) < 1:
            return

        # collecting all finished children
        for pid in list(self.active_children.keys()):
            p = None
            try:
                p, status = os.waitpid(pid, os.WNOHANG)
            except os.error:
                pass
            if p:
                self._deregister_child(pid)

        return

    #--------------------------------------------------------------------------
    def _deregister_child(self, pid):
        '''
        Deleting the child process with the given PID from self.active_children
        and from self.child_ids.

        @param pid: PID of child process to deregister
        @type pid:  int
        '''

        if not pid:
            return

        pid = int(pid)

        if self.verbose > 3:
            log.debug(_("Removing child %d from active child list ..."), pid)

        if pid not in self.active_children:
            return

        child_id = self.active_children[pid]
        del self.active_children[pid]

        if child_id in self.child_ids:
            del self.child_ids[child_id]

    #--------------------------------------------------------------------------
    def become_child(self):
        """
        Fork a new subprocess.

        @return: True, if it is now the child process,
                 False, if it is the parent process.
        @rtype: bool

        """

        if self.verbose > 2:
            log.debug(_("Forking a child process ..."))

        self.collect_children()

        # find out the child ID for the new child process
        i = 1
        child_id = None
        while not child_id:
            if i not in self.child_ids:
                child_id = i
            else:
                i += 1

        # Doing the fork ...
        pid = os.fork()
        if pid:
            # Parent process
            if self.verbose > 2:
                log.debug(_("Forked with process ID %d."), pid)
            self.active_children[pid] = child_id
            self.child_ids[child_id] = pid
            return False

        # Child process.
        if self.verbose > 3:
            log.debug(_("And here is the child ..."))
        self.pidfile.auto_remove = False
        self._child_id = child_id
        self._is_child = True

        return True

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
