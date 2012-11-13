#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: A base handler module for a handler object, that can call or spawn
          OS commands and read and write files.
"""

# Standard modules
import sys
import os
import logging
import re
import datetime
import subprocess
import pwd
import grp
import pipes
import signal
import errno

from gettext import gettext as _

# Own modules
from pb_base.common import pp, caller_search_path

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError
from pb_base.errors import PbReadTimeoutError, PbWriteTimeoutError

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

__version__ = '0.2.0'

log = logging.getLogger(__name__)

# Some module varriables
CHOWN_CMD = os.sep + os.path.join('bin', 'chown')
ECHO_CMD = os.sep + os.path.join('bin', 'echo')
SUDO_CMD = os.sep + os.path.join('usr', 'bin', 'sudo')

#==============================================================================
class PbBaseHandlerError(PbBaseObjectError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#-------------------------------------------------------------------------------
class CommandNotFoundError(PbBaseHandlerError):
    """
    Special exception, if one ore more OS commands were not found.

    """

    #--------------------------------------------------------------------------
    def __init__(self, cmd_list):
        """
        Constructor.

        @param cmd_list: all not found OS commands.
        @type cmd_list: list

        """

        self.cmd_list = None
        if cmd_list is None:
            self.cmd_list = [_("Unknown OS command.")]
        elif isinstance(cmd_list, list):
            self.cmd_list = cmd_list
        else:
            self.cmd_list = [cmd_list]

        if len(self.cmd_list) < 1:
            raise ValueError(_("Empty command list given."))

    #--------------------------------------------------------------------------
    def __str__(self):
        """
        Typecasting into a string for error output.
        """

        cmds = ', '.join(map(lambda x: ("'" + str(x) + "'"), self.cmd_list))
        msg = "Could not found OS command"
        if len(self.cmd_list) != 1:
            msg += 's'
        msg += ": " + cmds
        return msg


#==============================================================================
class PbBaseHandler(PbBaseObject):
    """
    Base class for handler objects.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            appname = None,
            verbose = 0,
            version = __version__,
            base_dir = None,
            use_stderr = False,
            initialized = False,
            simulate = False,
            sudo = False,
            quiet = False,
            ):
        """
        Initialisation of the base handler object.

        @raise CommandNotFoundError: if the commands 'chmod', 'echo' and
                                     'sudo' could not be found.
        @raise PbBaseHandlerError: on a uncoverable error.

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
        @param simulate: don't execute actions, only display them
        @type simulate: bool
        @param sudo: should the command executed by sudo by default
        @type sudo: bool
        @param quiet: don't display ouput of action after calling
        @type quiet: bool

        @return: None
        """

        super(PbBaseHandler, self).__init__(
                appname = appname,
                verbose = verbose,
                version = version,
                base_dir = base_dir,
                use_stderr = use_stderr,
                initialized = False,
        )

        failed_commands = []

        self._simulate = bool(simulate)
        """
        @ivar: don't execute actions, only display them
        @type: bool
        """

        self._quiet = quiet
        """
        @ivar: don't display ouput of action after calling
               (except output on STDERR)
        @type: bool
        """

        self._sudo = sudo
        """
        @ivar: should the command executed by sudo by default
        @type: bool
        """

        self._chown_cmd = CHOWN_CMD
        """
        @ivar: the chown command for changing ownership of file objects
        @type: str
        """
        if not os.path.exists(self.chown_cmd) or not os.access(
                self.chown_cmd, os.X_OK):
            self._chown_cmd = self.get_command('chown')
        if not self.chown_cmd:
            failed_commands.append('chown')

        self._echo_cmd = ECHO_CMD
        """
        @ivar: the echo command for simulating execution
        @type: str
        """
        if not os.path.exists(self.echo_cmd) or not os.access(
                self.echo_cmd, os.X_OK):
            self._echo_cmd = self.get_command('echo')
        if not self.echo_cmd:
            failed_commands.append('echo')

        self._sudo_cmd = SUDO_CMD
        """
        @ivar: the sudo command for execute commands as root
        @type: str
        """
        if not os.path.exists(self.sudo_cmd) or not os.access(
                self._sudo_cmd, os.X_OK):
            self.sudo_cmd = self.get_command('sudo')
        if not self.sudo_cmd:
            failed_commands.append('sudo')

        # Some commands are missing
        if failed_commands:
            raise CommandNotFoundError(failed_commands)

        self.initialized = True
        if self.verbose > 3:
            log.debug("Initialized.")

    #------------------------------------------------------------
    @property
    def simulate(self):
        """Simulation mode."""
        return self._simulate

    @simulate.setter
    def simulate(self, value):
        self._simulate = bool(value)

    #------------------------------------------------------------
    @property
    def quiet(self):
        """Don't display ouput of action after calling."""
        return self._quiet

    @quiet.setter
    def quiet(self, value):
        self._quiet = bool(value)

    #------------------------------------------------------------
    @property
    def sudo(self):
        """Should the command executed by sudo by default."""
        return self._sudo

    @sudo.setter
    def sudo(self, value):
        self._sudo = bool(value)

    #------------------------------------------------------------
    @property
    def chown_cmd(self):
        """The absolute path to the OS command 'chown'."""
        return self._chown_cmd

    #------------------------------------------------------------
    @property
    def echo_cmd(self):
        """The absolute path to the OS command 'echo'."""
        return self._echo_cmd

    #------------------------------------------------------------
    @property
    def sudo_cmd(self):
        """The absolute path to the OS command 'sudo'."""
        return self._sudo_cmd

    #--------------------------------------------------------------------------
    def get_command(self, cmd, quiet = False):
        """
        Searches the OS search path for the given command and gives back the
        normalized position of this command.
        If the command is given as an absolute path, it check the existence
        of this command.

        @param cmd: the command to search
        @type cmd: str
        @param quiet: No warning message, if the command could not be found,
                      only a debug message
        @type quiet: bool

        @return: normalized complete path of this command, or None,
                 if not found
        @rtype: str or None

        """

        if self.verbose > 2:
            log.debug("Searching for command '%s' ..." % (cmd))

        # Checking an absolute path
        if os.path.isabs(cmd):
            if not os.path.exists(cmd):
                log.warning("Command '%s' doesn't exists." % (cmd))
                return None
            if not os.access(cmd, os.X_OK):
                msg = ("Command '%s' is not executable." % (cmd))
                log.warning(msg)
                return None
            return os.path.normpath(cmd)

        # Checking a relative path
        for d in caller_search_path():
            if self.verbose > 3:
                log.debug("Searching command in '%s' ...", d)
            p = os.path.join(d, cmd)
            if os.path.exists(p):
                if self.verbose > 2:
                    log.debug("Found '%s' ..." % (p))
                if os.access(p, os.X_OK):
                    return os.path.normpath(p)
                else:
                    log.debug("Command '%s' is not executable.", p)

        # command not found, sorry
        if quiet:
            if self.verbose > 2:
                log.debug("Command '%s' not found.", cmd)
        else:
            log.warning("Command '%s' not found.", cmd)

        return None

    #--------------------------------------------------------------------------
    def call(self,
            cmd,
            sudo = None,
            simulate = None,
            quiet = None,
            shell = False,
            stdout = None,
            stderr = None,
            bufsize = 0,
            drop_stderr = False,
            close_fds = False,
            **kwargs ):
        """
        Executing a OS command.

        @param cmd: the cmd you wanne call
        @type cmd: list of strings or str
        @param sudo: execute the command with sudo
        @type sudo: bool (or none, if self.sudo will be be asked)
        @param simulate: simulate execution or not,
                         if None, self.simulate will asked
        @type simulate: bool or None
        @param quiet: quiet execution independend of self.quiet
        @type quiet: bool
        @param shell: execute the command with a shell
        @type shell: bool
        @param stdout: file descriptor for stdout,
                       if not given, self.stdout is used
        @type stdout: int
        @param stderr: file descriptor for stderr,
                       if not given, self.stderr is used
        @type stderr: int
        @param bufsize: size of the buffer for stdout
        @type bufsize: int
        @param drop_stderr: drop all output on stderr, independend
                            of any value of stderr
        @type drop_stderr: bool
        @param close_fds: closing all open file descriptors
                          (except 0, 1 and 2) on calling subprocess.Popen()
        @type close_fds: bool
        @param kwargs: any optional named parameter (must be one
            of the supported suprocess.Popen arguments)
        @type kwargs: dict

        @return: tuple of::
            - return value of calling process,
            - output on STDOUT,
            - output on STDERR

        """

        cmd_list = cmd
        if isinstance(cmd, basestring):
            cmd_list = [cmd]

        pwd_info = pwd.getpwuid(os.geteuid())

        if sudo is None:
            sudo = self.sudo
        if sudo:
            cmd_list.insert(0, self.sudo_cmd)

        if simulate is None:
            simulate = self.simulate

        if simulate:
            cmd_list.insert(0, self.echo_cmd)
            quiet = False

        if quiet is None:
            quiet = self.quiet

        use_shell = bool(shell)

        cmd_list = [str(element) for element in cmd_list]
        log.debug("Executing %r", cmd_list)

        if quiet and self.verbose > 1:
            log.debug("Quiet execution")

        used_stdout = subprocess.PIPE
        if stdout is not None:
            used_stdout = stdout

        used_stderr = subprocess.PIPE
        if drop_stderr:
            used_stderr = None
        elif stderr is not None:
            used_stderr = stderr

        cmd_obj = subprocess.Popen(
            cmd_list,
            shell = use_shell,
            cwd = self.base_dir,
            close_fds = close_fds,
            stderr = used_stderr,
            stdout = used_stdout,
            bufsize = bufsize,
            env = {'USER': pwd_info.pw_name},
            **kwargs
        )

        # Display Output of executable
        stdoutdata = ''
        stderrdata = ''
        (stdoutdata, stderrdata) = cmd_obj.communicate()

        if stderrdata:
            if quiet and not self.verbose:
                pass
            else:
                msg = "Output on StdErr: '%s'." % (stderrdata.strip())
                if quiet:
                    log.debug(msg)
                else:
                    self.handle_error(msg, self.appname)

        if stdoutdata:
            do_out = False
            if self.verbose:
                if quiet:
                    if self.verbose > 3:
                        do_out = True
                    else:
                        do_out = False
                else:
                    do_out = True
            else:
                if not quiet:
                    do_out = True
            if do_out:
                log.debug("Output on StdOut: %r", stdoutdata.strip())

        ret = cmd_obj.wait()
        log.debug("Returncode: %s" % (ret))

        return (ret, stdoutdata, stderrdata)

    #--------------------------------------------------------------------------
    def read_file(self, filename, timeout = 2, quiet = False):
        """
        Reads the content of the given filename.

        @raise IOError: if file doesn't exists or isn't readable
        @raise PbReadTimeoutError: on timeout reading the file

        @param filename: name of the file to read
        @type filename: str
        @param timeout: the amount in seconds when this method should timeout
        @type timeout: int
        @param quiet: increases the necessary verbosity level to
                      put some debug messages
        @type quiet: bool

        @return: file content
        @rtype:  str

        """

        needed_verbose_level = 1
        if quiet:
            needed_verbose_level = 3

        def read_alarm_caller(signum, sigframe):
            '''
            This nested function will be called in event of a timeout

            @param signum:   the signal number (POSIX) which happend
            @type signum:    int
            @param sigframe: the frame of the signal
            @type sigframe:  object
            '''

            raise PbReadTimeoutError(timeout, filename)

        timeout = abs(int(timeout))

        if not os.path.isfile(filename):
            raise IOError(errno.ENOENT, "File dosn't exists", filename)
        if not os.access(filename, os.R_OK):
            raise IOError(errno.EACCES, 'Read permission denied', filename)

        if self.verbose > needed_verbose_level:
            log.debug("Reading content of %r ...", filename)

        signal.signal(signal.SIGALRM, read_alarm_caller)
        signal.alarm(timeout)

        content = ''
        fh = open(filename, 'r')
        for line in fh.readlines():
            content += line
        fh.close()

        signal.alarm(0)

        return content

    #--------------------------------------------------------------------------
    def write_file(self, filename, content,
            timeout = 2, must_exists = True, quiet = False):
        """
        Writes the given content into the given filename.
        It should only be used for small things, because it writes unbuffered.

        @raise IOError: if file doesn't exists or isn't writeable
        @raise PbWriteTimeoutError: on timeout writing into the file

        @param filename: name of the file to write
        @type filename: str
        @param content: the content to write into the file
        @type content: str
        @param timeout: the amount in seconds when this method should timeout
        @type timeout: int
        @param must_exists: the file must exists before writing
        @type must_exists: bool
        @param quiet: increases the necessary verbosity level to
                      put some debug messages
        @type quiet: bool

        @return: None

        """

        def write_alarm_caller(signum, sigframe):
            '''
            This nested function will be called in event of a timeout

            @param signum:   the signal number (POSIX) which happend
            @type signum:    int
            @param sigframe: the frame of the signal
            @type sigframe:  object
            '''

            raise PbWriteTimeoutError(timeout, filename)

        verb_level1 = 0
        verb_level2 = 1
        verb_level3 = 3
        if quiet:
            verb_level1 = 2
            verb_level2 = 3
            verb_level3 = 4

        timeout = int(timeout)

        if must_exists:
            if not os.path.isfile(filename):
                raise IOError(errno.ENOENT, "File dosn't exists", filename)

        if os.path.exists(filename):
            if not os.access(filename, os.W_OK):
                if self.simulate:
                    log.error("Write permission to %r denied", filename)
                else:
                    raise IOError(errno.EACCES,
                            'Write permission denied', filename)
        else:
            parent_dir = os.path.dirname(filename)
            if not os.access(parent_dir, os.W_OK):
                if self.simulate:
                    log.error("Write permission to %r denied", parent_dir)
                else:
                    raise IOError(errno.EACCES,
                            'Write permission denied', parent_dir)

        if self.verbose > verb_level1:
            log.debug("Writing %r ...", filename)
        if self.verbose > verb_level2:
            log.debug("Write %r into %r.", content, filename)

        if self.simulate:
            if self.verbose > verb_level2:
                log.debug("Simulating write into %r.", filename)
            return

        signal.signal(signal.SIGALRM, write_alarm_caller)
        signal.alarm(timeout)

        # Open filename for writing unbuffered
        if self.verbose > verb_level3:
            log.debug("Opening '%s' for write unbuffered ...", filename)
        fh = open(filename, 'w', 0)

        try:
            fh.write(content)
        finally:
            if self.verbose > verb_level3:
                log.debug("Closing '%s' ...", filename)
            fh.close()

        signal.alarm(0)

        return


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
