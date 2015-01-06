#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2015 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unut tests on base object
'''

import os
import sys
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger('test_errors')


#==============================================================================

class TestPbErrors(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.errors ...")
        import pb_base.errors
        from pb_base.errors import PbError, FunctionNotImplementedError
        from pb_base.errors import PbIoTimeoutError, PbReadTimeoutError
        from pb_base.errors import PbWriteTimeoutError

    #--------------------------------------------------------------------------
    def test_pb_error(self):

        log.info("Test raising a PbError exception ...")

        import pb_base.errors
        from pb_base.errors import PbError

        with self.assertRaises(PbError) as cm:
            raise PbError("Bla blub")
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_func_not_implemented(self):

        log.info("Test raising a FunctionNotImplementedError exception ...")

        import pb_base.errors
        from pb_base.errors import FunctionNotImplementedError

        with self.assertRaises(FunctionNotImplementedError) as cm:
            raise FunctionNotImplementedError(
                    'test_func_not_implemented', 'test_errors')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_io_timeout_error(self):

        log.info("Test raising a PbIoTimeoutError exception ...")

        import pb_base.errors
        from pb_base.errors import PbIoTimeoutError

        with self.assertRaises(PbIoTimeoutError) as cm:
            raise PbIoTimeoutError("Test IO error", 2.5, '/etc/shadow')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_read_timeout_error(self):

        log.info("Test raising a PbReadTimeoutError exception ...")

        import pb_base.errors
        from pb_base.errors import PbReadTimeoutError

        with self.assertRaises(PbReadTimeoutError) as cm:
            raise PbReadTimeoutError(2.55, '/etc/shadow')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_write_timeout_error(self):

        log.info("Test raising a PbWriteTimeoutError exception ...")

        import pb_base.errors
        from pb_base.errors import PbWriteTimeoutError

        with self.assertRaises(PbWriteTimeoutError) as cm:
            raise PbWriteTimeoutError(5, '/etc/shadow')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPbErrors('test_import', verbose))
    suite.addTest(TestPbErrors('test_pb_error', verbose))
    suite.addTest(TestPbErrors('test_func_not_implemented', verbose))
    suite.addTest(TestPbErrors('test_io_timeout_error', verbose))
    suite.addTest(TestPbErrors('test_read_timeout_error', verbose))
    suite.addTest(TestPbErrors('test_write_timeout_error', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
