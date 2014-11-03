#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on crc module
"""

import unittest
import os
import sys
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger(__name__)


#==============================================================================

class TestPbCrc(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):

        self.test_str = '7a608ad6-8ada-4b76-9fde-05c6d1420907'

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.crc ...")
        import pb_base.crc

    #--------------------------------------------------------------------------
    def test_checksum(self):

        log.info("Testing checksum() from pb_base.crc ...")

        import pb_base.crc
        cksum = pb_base.crc.checksum(self.test_str)
        log.debug("checksum(%r): %r", self.test_str, cksum)
        self.assertEqual(cksum, 2423)

    #--------------------------------------------------------------------------
    def test_checksum256(self):

        log.info("Testing checksum256() from pb_base.crc ...")

        import pb_base.crc
        cksum = pb_base.crc.checksum256(self.test_str)
        log.debug("checksum256(%r): %r", self.test_str, cksum)
        self.assertEqual(cksum, 119)

    #--------------------------------------------------------------------------
    def test_crc64(self):

        log.info("Testing crc64() from pb_base.crc ...")

        import pb_base.crc
        cksum = pb_base.crc.crc64(self.test_str)
        log.debug("crc64(%r): %r", self.test_str, cksum)
        self.assertEqual(cksum, (1792271819, 3547210208))

    #--------------------------------------------------------------------------
    def test_crc64_digest(self):

        log.info("Testing crc64_digest() from pb_base.crc ...")

        import pb_base.crc
        cksum = pb_base.crc.crc64_digest(self.test_str)
        log.debug("crc64_digest(%r): %r", self.test_str, cksum)
        self.assertEqual(cksum, '6ad3e5cbd36e21e0')

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPbCrc('test_checksum', verbose))
    suite.addTest(TestPbCrc('test_checksum256', verbose))
    suite.addTest(TestPbCrc('test_crc64', verbose))
    suite.addTest(TestPbCrc('test_crc64_digest', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
