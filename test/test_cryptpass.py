#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on the cryptpass module
'''

import unittest
import os
import sys
import logging
import re

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger(__name__)

#==============================================================================

class TestCryptPass(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.cryptpass ...")
        import pb_base.cryptpass
        from pb_base.cryptpass import gensalt, shadowcrypt, valid_hash_algos

    #--------------------------------------------------------------------------
    def test_gensalt(self):

        log.info("Testing generation of a salt string.")

        import pb_base.cryptpass
        from pb_base.cryptpass import gensalt, shadowcrypt, valid_hash_algos

        log.debug("Generation of a valid 8-character salt ...")
        salt = gensalt(8)
        log.debug("Generated salt: %r", salt)
        self.assertIsInstance(salt, str,
                "Generated salt must be from class 'basetring'.")
        self.assertEqual(len(salt), 8,
                "Generated salt must consists of eight characters.")
        msg = ("Generated salt may only consists of numbers, lowercase " +
                "uppercase letters, the dot ('.') character and the " +
                "slash character ('/').")
        if sys.version_info[0] > 2:
            self.assertNotRegex(salt, r'[^0-9a-zA-Z\.\/]', msg)
        else:
            self.assertNotRegexpMatches(salt, r'[^0-9a-zA-Z\.\/]', msg)

        for length in ('bla', 0, -10):
            log.debug("Generation of a salt with an invalid length %r.", length)
            with self.assertRaises(ValueError) as cm:
                salt = gensalt(length)
            e = cm.exception
            log.debug("'ValueError' raised on invalid length %r: %s", length, e)

    #--------------------------------------------------------------------------
    def test_shadowcrypt_valid(self):

        pwd = "TestTest"

        log.info("Encrypting password %r with a random generated salt.", pwd)

        import pb_base.cryptpass
        from pb_base.cryptpass import gensalt, shadowcrypt, valid_hash_algos

        for algo in ('crypt', 'md5', 'sha256', 'sha512'):
            log.debug("Encrypting with algorithm %r ...", algo)
            crypted = shadowcrypt(pwd, algo)
            log.debug("Encrypted password: %r", crypted)
            self.assertIsInstance(crypted, str,
                    "Encrypted password must be from class 'basetring'.")

        log.info("Encrypting password %r with a given salt.", pwd)
        for algo in ('crypt', 'md5', 'sha256', 'sha512'):
            algo_nr = valid_hash_algos[algo]
            log.debug("Encrypting with algorithm %r (%r)...", algo, algo_nr)
            length = 8
            if algo == 'crypt':
                length = 2
            salt = gensalt(length)
            salt2use = salt
            if algo != 'crypt':
                salt2use = '$%d$%s$' % (algo_nr, salt)

            log.debug("Encrypting with simple salt %r ...", salt)
            crypted = shadowcrypt(pwd, algo, salt = salt)
            log.debug("Encrypted password: %r", crypted)
            self.assertIsInstance(crypted, str,
                    "Encrypted password must be from class 'basetring'.")
            self.assertGreater(len(crypted), length, (("The encrypted " +
                    "password must be longer than the length of salt %d.") % (
                        length)))
            salt_pattern = r'^%s' % (re.escape(salt2use))
            self.assertRegexpMatches(crypted, salt_pattern, (("The salt %r " +
                    "must be embedded at the beginning of the ecrypted " +
                    "password %r.") % (salt2use, crypted)))

            log.debug("Encrypting with complete salt %r ...", salt2use)
            crypted2 = shadowcrypt(pwd, algo, salt = salt2use)
            self.assertEqual(crypted, crypted2, (("Encrypted password with " +
                    "simple salt %r (-> %r) must be identic with the " +
                    " encrypted password with the complete salt %r (-> %r).") %
                    (salt, crypted, salt2use, crypted2)))

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestCryptPass('test_import', verbose))
    suite.addTest(TestCryptPass('test_gensalt', verbose))
    suite.addTest(TestCryptPass('test_shadowcrypt_valid', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
