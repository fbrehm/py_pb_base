#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on base object
'''

import unittest
import os
import sys
import time
import re
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger(__name__)

# Some predefined module variables / constants
pidfile_normal = 'test_pidfile.pid'
pidfile_forbidden = '/root/test_pidfile.pid'
pidfile_invalid = '/bla/blub/blubber.pid'

#==============================================================================
def file_content(filename):

    if not os.path.isfile(filename):
        sys.stderr.write("File '%s' doesn't exists.\n" % (filename))
        return None

    fh = None
    content = None
    try:
        fh = open(filename)
        content = ''.join(fh.readlines())
    except IOError as e:
        sys.stderr.write("Could not read file '%s': %s\n" % (filename, str(e)))
    finally:
        if fh:
            fh.close()

    return content

#==============================================================================

class TestPidFile(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.pidfile ...")

        import pb_base.pidfile
        log.debug("Module %r imported.", 'pb_base.pidfile')

        from pb_base.pidfile import PidFileError
        log.debug("Exception class %r from module %r imported.",
                'PidFileError', 'pb_base.pidfile')

        from pb_base.pidfile import InvalidPidFileError
        log.debug("Exception class %r from module %r imported.",
                'InvalidPidFileError', 'pb_base.pidfile')

        from pb_base.pidfile import PidFileInUseError
        log.debug("Exception class %r from module %r imported.",
                'PidFileInUseError', 'pb_base.pidfile')

        from pb_base.pidfile import PidFile
        log.debug("Class %r from module %r imported.",
                'PidFile', 'pb_base.pidfile')


        import pb_base.object

    #--------------------------------------------------------------------------
    def test_object(self):

        log.info("Testing init of a simple object.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile

        pid_file = PidFile(
            filename = pidfile_normal,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )
        log.debug("PidFile %%r: %r", pid_file)
        log.debug("PidFile %%s: %s", str(pid_file))

    #--------------------------------------------------------------------------
    def test_no_filename(self):

        log.info("Testing fail init of a PidFile object without a filename.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile

        with self.assertRaises(ValueError) as cm:
            pid_file = PidFile(
                filename = '',
                appname = 'test_pidfile',
                verbose = self.verbose,
            )
            log.debug("PidFile %%s: %s", str(pid_file))
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_create_normal(self):

        log.info("Test creating of a normal PID file.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile

        pid_file = PidFile(
            filename = pidfile_normal,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )

        try:
            pid_file.create()
            if not pid_file.created:
                self.fail("Pidfile %r seems not to be created.",
                        pidfile_normal)
            if not os.path.exists(pidfile_normal):
                self.fail("Pidfile %r not created.", pidfile_normal)
            fcontent = file_content(pidfile_normal)
            if fcontent is None:
                self.fail("Could not read pidfile %r.", pidfile_normal)
            elif not fcontent:
                self.fail("Pidfile %r seems to be empty.", pidfile_normal)
            else:
                match = re.search(r'^\s*(\d+)\s*$', fcontent)
                if not match:
                    self.fail("Pidfile %r with invalid content: %r",
                            pidfile_normal, fcontent)
                else:
                    pid = int(match.group(1))
                    if pid == os.getpid():
                        log.debug("Found correct PID %d in %r.",
                                pid, pidfile_normal)
                    else:
                        self.fail("Found invalid PID %d in %r, but should be %d.",
                                pid, pidfile_normal, os.getpid())
        finally:
            del pid_file

    #--------------------------------------------------------------------------
    @unittest.skipIf(os.geteuid() <= 0, "Test skipped as root")
    def test_create_forbidden(self):

        log.info("Test fail creating of a PID file on a forbidden place.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile
        from pb_base.pidfile import InvalidPidFileError

        pid_file = PidFile(
            filename = pidfile_forbidden,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )

        try:
            with self.assertRaises(InvalidPidFileError) as cm:
                pid_file.create()
            e = cm.exception
            log.debug("%s raised: %s", e.__class__.__name__, e)

        finally:
            del pid_file

    #--------------------------------------------------------------------------
    def test_create_invalid(self):

        log.info("Test fail creating of a PID file with an invalid path.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile
        from pb_base.pidfile import InvalidPidFileError

        pid_file = PidFile(
            filename = pidfile_invalid,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )

        try:
            with self.assertRaises(InvalidPidFileError) as cm:
                pid_file.create()
            e = cm.exception
            log.debug("%s raised: %s", e.__class__.__name__, e)

        finally:
            del pid_file

    #--------------------------------------------------------------------------
    def test_create_concurrent(self):

        log.info("Test fail creating of concurrent  PID files.")

        import pb_base.pidfile
        from pb_base.pidfile import PidFile
        from pb_base.pidfile import PidFileInUseError

        carry_on = True

        pid_file1 = PidFile(
            filename = pidfile_normal,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )
        pid_file2 = PidFile(
            filename = pidfile_normal,
            appname = 'test_pidfile',
            verbose = self.verbose,
        )

        try:
            pid_file1.create()

            with self.assertRaises(PidFileInUseError) as cm:
                pid_file2.create()
            e = cm.exception
            log.debug("%s raised: %s", e.__class__.__name__, e)

        finally:
            del pid_file2
            del pid_file1

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPidFile('test_import', verbose))
    suite.addTest(TestPidFile('test_object', verbose))
    suite.addTest(TestPidFile('test_no_filename', verbose))
    suite.addTest(TestPidFile('test_create_normal', verbose))
    suite.addTest(TestPidFile('test_create_forbidden', verbose))
    suite.addTest(TestPidFile('test_create_invalid', verbose))
    suite.addTest(TestPidFile('test_create_concurrent', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
