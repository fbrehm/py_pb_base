#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unut tests on base object
'''

import unittest
import os
import sys
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

import pb_base.errors

log = logging.getLogger(__name__)


#==============================================================================

class TestPbErrors(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_pb_error(self):

        try:
            raise pb_base.errors.PbError("Bla blub")
        except Exception as e:
            if not isinstance(e, pb_base.errors.PbError):
                self.fail("Could not raise a PbError exception by a %s: %s" % (
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_func_not_implemented(self):

        try:
            raise pb_base.errors.FunctionNotImplementedError(
                    'test_func_not_implemented', 'test_errors'
            )
        except Exception as e:
            if not isinstance(e, pb_base.errors.FunctionNotImplementedError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'FunctionNotImplementedError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_io_timeout_error(self):

        try:
            raise pb_base.errors.PbIoTimeoutError(
                    "Test IO error", 2.5, '/etc/shadow')
        except Exception as e:
            if not isinstance(e, pb_base.errors.PbIoTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbIoTimeoutError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_read_timeout_error(self):

        try:
            raise pb_base.errors.PbReadTimeoutError( 2.55, '/etc/shadow')
        except Exception as e:
            if not isinstance(e, pb_base.errors.PbReadTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbReadTimeoutError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_write_timeout_error(self):

        try:
            raise pb_base.errors.PbWriteTimeoutError( 2.45, '/etc/shadow')
        except Exception as e:
            if not isinstance(e, pb_base.errors.PbWriteTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbWriteTimeoutError',
                        e.__class__.__name__, str(e)))

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPbErrors('test_pb_error', verbose))
    suite.addTest(TestPbErrors('test_func_not_implemented', verbose))
    suite.addTest(TestPbErrors('test_io_timeout_error', verbose))
    suite.addTest(TestPbErrors('test_read_timeout_error', verbose))
    suite.addTest(TestPbErrors('test_write_timeout_error', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
