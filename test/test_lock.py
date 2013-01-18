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
            verbose = 1,
            lockdir = '/tmp',
        )
        log.debug("PbLockHandler %%s: %s", str(locker))

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

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
