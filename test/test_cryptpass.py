#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on the cryptpass module
'''

import unittest
import os
import sys
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

from pb_base.cryptpass import gensalt, shadowcrypt

log = logging.getLogger(__name__)

#==============================================================================

class TestCryptPass(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_gensalt(self):

        log.info("Testing generation of a salt string.")

        log.debug("Generation of a valid 8-character salt ...")
        salt = gensalt(8)
        log.debug("Generated salt: %r", salt)
        self.assertIsInstance(salt, basestring,
                "Generated salt must be from class 'basetring'.")
        self.assertEqual(len(salt), 8,
                "Generated salt must consists of eight characters.")
        self.assertNotRegexpMatches(salt, r'[^0-9a-zA-Z\.\/]',
                ("Generated salt may only consists of numbers, lowercase " +
                 "uppercase letters, the dot ('.') character and the " +
                 "slash character ('/')."))

        for length in ('bla', 0, -10):
            log.debug("Generation of a salt with an invalid length %r.", length)
            with self.assertRaises(ValueError) as cm:
                salt = gensalt(length)
            e = cm.exception
            log.debug("'ValueError' raised on invalid length %r: %s", length, e)

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    init_root_logger(verbose)

    log.info("Starting tests ...")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromName(
            'test_cryptpass.TestCryptPass.test_gensalt'))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
