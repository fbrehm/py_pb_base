#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on locking handler object
'''

import unittest
import os
import sys
import logging
import tempfile

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

import pb_base.object
from pb_base.object import PbBaseObjectError

import pb_base.handler.lock

from pb_base.handler.lock import LockHandlerError
from pb_base.handler.lock import LockdirNotExistsError, LockdirNotWriteableError
from pb_base.handler.lock import PbLockHandler

log = logging.getLogger(__name__)

#==============================================================================

class TestPbLockHandler(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def create_lockfile(self, content):

        (fd, filename) = tempfile.mkstemp()

        os.write(fd, "{!s}".format(content))
        os.close(fd)

        return filename

    #--------------------------------------------------------------------------
    def remove_lockfile(self, filename):

        if os.path.exists(filename):
            log.debug("Removing {!r} ...".format(filename))
            os.remove(filename)
        else:
            log.debug("Lockfile {!r} doesn't exists.".format(filename))

    #--------------------------------------------------------------------------
    def test_object(self):

        log.info("Testing init of a simple object.")
        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 1,
            lockdir = '/tmp',
        )
        log.debug("PbLockHandler %%r: %r", locker)
        log.debug("PbLockHandler %%s: %s", str(locker))

    #--------------------------------------------------------------------------
    def test_simple_lockfile(self):

        log.info("Testing creation and removing of a simple lockfile.")

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
            lockdir = '/tmp',
        )
        locker.create_lockfile('bla.lock')
        locker.remove_lockfile('bla.lock')

    #--------------------------------------------------------------------------
    def test_lockobject(self):

        log.info("Testing lock object on creation of a simple lockfile.")

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
        )
        lock = locker.create_lockfile('bla.lock')
        log.debug("PbLock object %%r: %r", lock)
        log.debug("PbLock object %%s: %s", str(lock))
        locker.remove_lockfile('bla.lock')

    #--------------------------------------------------------------------------
    def test_invalid_dir(self):

        log.info("Testing creation lockfile in an invalid lock directory.")

        ldir = '/etc/passwd'
        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
            lockdir = ldir,
        )
        with self.assertRaises(LockdirNotExistsError) as cm:
            locker.create_lockfile('bla.lock')
        e = cm.exception
        log.debug("{!s} raised on lockdir = {!r}: {!s}".format(
                'LockdirNotExistsError', ldir, e))
        del locker

        if os.getegid():
            ldir = '/var'
            locker = PbLockHandler(
                appname = 'test_base_object',
                verbose = 3,
                lockdir = ldir,
            )
            with self.assertRaises(LockdirNotWriteableError) as cm:
                locker.create_lockfile('bla.lock')
            e = cm.exception
            log.debug("{!s} raised on lockdir = {!r}: {!s}".format(
                    'LockdirNotWriteableError', ldir, e))

    #--------------------------------------------------------------------------
    def test_valid_lockfile(self):

        log.info("Testing fail on creation lockfile with a valid PID.")

        content = "{:d}\n".format(os.getpid())

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
            lockdir = '/tmp',
        )

        lockfile = self.create_lockfile(content)
        try:
            result = locker.create_lockfile(
                lockfile,
                delay_start = 0.2,
                delay_increase = 0.4,
                max_delay = 5
            )
            if result:
                self.fail("PbLockHandler shouldn't be able to create the lockfile.")
        finally:
            self.remove_lockfile(lockfile)

    #--------------------------------------------------------------------------
    def test_invalid_lockfile1(self):

        log.info("Testing creation lockfile with an invalid previous lockfile #1.")

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
        )

        content = "\n\n"
        lockfile = self.create_lockfile(content)
        try:
            result = locker.create_lockfile(
                lockfile,
                delay_start = 0.2,
                delay_increase = 0.4,
                max_delay = 5
            )
            locker.remove_lockfile(lockfile)
            if result:
                self.fail("PbLockHandler should not be able to create the lockfile.")
        finally:
            self.remove_lockfile(lockfile)

    #--------------------------------------------------------------------------
    def test_invalid_lockfile2(self):

        log.info("Testing creation lockfile with an invalid previous lockfile #2.")

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
        )

        content = "Bli bla blub\n\n"
        lockfile = self.create_lockfile(content)
        try:
            result = locker.create_lockfile(
                lockfile,
                delay_start = 0.2,
                delay_increase = 0.4,
                max_delay = 5
            )
            locker.remove_lockfile(lockfile)
            if result:
                self.fail("PbLockHandler should not be able to create the lockfile.")
        finally:
            self.remove_lockfile(lockfile)

    #--------------------------------------------------------------------------
    def test_invalid_lockfile3(self):

        log.info("Testing creation lockfile with an invalid previous lockfile #3.")

        locker = PbLockHandler(
            appname = 'test_base_object',
            verbose = 3,
        )

        content = "123456\n\n"
        lockfile = self.create_lockfile(content)
        try:
            result = locker.create_lockfile(
                lockfile,
                delay_start = 0.2,
                delay_increase = 0.4,
                max_delay = 5
            )
            locker.remove_lockfile(lockfile)
            if not result:
                self.fail("PbLockHandler should be able to create the lockfile.")
        finally:
            self.remove_lockfile(lockfile)

#==============================================================================


if __name__ == '__main__':

    verbose = get_arg_verbose()
    init_root_logger(verbose)

    log.info("Starting tests ...")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_object'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_simple_lockfile'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_invalid_dir'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_valid_lockfile'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_lockobject'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_invalid_lockfile1'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_invalid_lockfile2'))
    suite.addTests(loader.loadTestsFromName(
            'test_lock.TestPbLockHandler.test_invalid_lockfile3'))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
