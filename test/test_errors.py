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

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import pb_base.errors


#==============================================================================

class TestPbErrors(unittest.TestCase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_pb_error(self):

        try:
            raise pb_base.errors.PbError("Bla blub")
        except Exception, e:
            if not isinstance(e, pb_base.errors.PbError):
                self.fail("Could not raise a PbError exception by a %s: %s" % (
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_func_not_implemented(self):

        try:
            raise pb_base.errors.FunctionNotImplementedError(
                    'test_func_not_implemented', 'test_errors'
            )
        except Exception, e:
            if not isinstance(e, pb_base.errors.FunctionNotImplementedError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'FunctionNotImplementedError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_io_timeout_error(self):

        try:
            raise pb_base.errors.PbIoTimeoutError(
                    "Test IO error", 2.5, '/etc/shadow')
        except Exception, e:
            if not isinstance(e, pb_base.errors.PbIoTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbIoTimeoutError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_read_timeout_error(self):

        try:
            raise pb_base.errors.PbReadTimeoutError( 2.55, '/etc/shadow')
        except Exception, e:
            if not isinstance(e, pb_base.errors.PbReadTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbReadTimeoutError',
                        e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_write_timeout_error(self):

        try:
            raise pb_base.errors.PbWriteTimeoutError( 2.45, '/etc/shadow')
        except Exception, e:
            if not isinstance(e, pb_base.errors.PbWriteTimeoutError):
                self.fail("Could not raise a %s exception by a %s: %s" % (
                        'PbWriteTimeoutError',
                        e.__class__.__name__, str(e)))

#==============================================================================

if __name__ == '__main__':

    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-v", "--verbose", action = "count",
            dest = 'verbose', help = 'Increase the verbosity level')
    args = arg_parser.parse_args()

    unittest.main(verbosity = args.verbose)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
