#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on crc module
'''

import unittest
import os
import sys

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import pb_base.crc


#==============================================================================

class TestPbCrc(unittest.TestCase):

    #--------------------------------------------------------------------------
    def setUp(self):

        self.test_str = '7a608ad6-8ada-4b76-9fde-05c6d1420907'

    #--------------------------------------------------------------------------
    def test_checksum(self):

        cksum = pb_base.crc.checksum(self.test_str)
        print "checksum(%r): %r" % (self.test_str, cksum)
        self.assertEqual(cksum, 2423)

    #--------------------------------------------------------------------------
    def test_checksum256(self):

        cksum = pb_base.crc.checksum256(self.test_str)
        print "checksum256(%r): %r" % (self.test_str, cksum)
        self.assertEqual(cksum, 119)

    #--------------------------------------------------------------------------
    def test_crc64(self):

        cksum = pb_base.crc.crc64(self.test_str)
        print "crc64(%r): %r" % (self.test_str, cksum)
        self.assertEqual(cksum, (1792271819L, 3547210208L))

    #--------------------------------------------------------------------------
    def test_crc64_digest(self):

        cksum = pb_base.crc.crc64_digest(self.test_str)
        print "crc64_digest(%r): %r" % (self.test_str, cksum)
        self.assertEqual(cksum, '6ad3e5cbd36e21e0')

#==============================================================================

if __name__ == '__main__':

    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-v", "--verbose", action = "count",
            dest = 'verbose', help = 'Increase the verbosity level')
    args = arg_parser.parse_args()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromName(
            'test_crc.TestPbCrc.test_checksum'))
    suite.addTests(loader.loadTestsFromName(
            'test_crc.TestPbCrc.test_checksum256'))
    suite.addTests(loader.loadTestsFromName(
            'test_crc.TestPbCrc.test_crc64'))
    suite.addTests(loader.loadTestsFromName(
            'test_crc.TestPbCrc.test_crc64_digest'))

    runner = unittest.TextTestRunner(verbosity = args.verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
