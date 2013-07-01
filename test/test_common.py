#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on common.py
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

class TestPbCommon(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.common ...")
        import pb_base.common

    #--------------------------------------------------------------------------
    def test_human2mbytes(self):

        log.info("Testing human2mbytes() from pb_base.common ...")

        import pb_base.common
        from pb_base.common import human2mbytes

        test_pairs_int_si = (
            ('1048576', 1),
            ('1MiB', 1),
            ('1 MiB', 1),
            ('1 MiB', 1),
            (' 1 MiB	', 1),
            ('1.2 MiB', int(1.2)),
            ('1 GiB', 1024),
            ('1 GB', 953),
            ('1.2 GiB', int(1.2 * 1024)),
            ('102400 KB', 100),
            ('100000 KB', 97),
            ('102400 MB', 1024 * 1000 * 1000 * 100 / 1024 / 1024),
            ('100000 MB', 1000 * 1000 * 1000 * 100 / 1024 / 1024),
            ('102400 MiB', 1024 * 100),
            ('100000 MiB', 1000 * 100),
            ('102400 GB', 1024 * 1000 * 1000 * 1000 * 100 / 1024 / 1024),
            ('100000 GB', 1000 * 1000 * 1000 * 1000 * 100 / 1024 / 1024),
            ('102400 GiB', 1024 * 1024 * 100),
            ('100000 GiB', 1024 * 1000 * 100),
            ('1024 TB', 1024 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1000 TB', 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1024 TiB', 1024 * 1024 * 1024),
            ('1000 TiB', 1024 * 1024 * 1000),
            ('1024 PB', 1024 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1000 PB', 1000 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1024 PiB', 1024 * 1024 * 1024 * 1024),
            ('1000 PiB', 1024 * 1024 * 1024 * 1000),
            ('1024 EB', 1024 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1000 EB', 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1024 EiB', 1024 * 1024 * 1024 * 1024 * 1024),
            ('1000 EiB', 1024 * 1024 * 1024 * 1024 * 1000),
            ('1024 ZB', 1024 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1000 ZB', 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 / 1024 / 1024),
            ('1024 ZiB', 1024 * 1024 * 1024 * 1024 * 1024 * 1024),
            ('1000 ZiB', 1024 * 1024 * 1024 * 1024 * 1024 * 1000),
        )

        for pair in test_pairs_int_si:

            src = pair[0]
            expected = pair[1]
            if self.verbose > 1:
                log.debug("Testing human2mbytes(%r) => %d", src, expected)
            result = human2mbytes(src, si_conform = True)
            if self.verbose > 1:
                log.debug("Got result: %r", result)
            self.assertIsInstance(result, int)
            self.assertEqual(expected, result)

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPbCommon('test_import', verbose))
    suite.addTest(TestPbCommon('test_human2mbytes', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
