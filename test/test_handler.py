#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2014 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on base handler object
          and df and fuser handler objects
"""

import unittest
import os
import sys
import logging
import tempfile
import time

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger(__name__)

#==============================================================================

class TestPbBaseHandler(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def tearDown(self):
        pass

    #--------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.handler ...")
        import pb_base.handler

        log.info("Testing import of PbBaseHandlerError from pb_base.handler ...")
        from pb_base.handler import PbBaseHandlerError

        log.info("Testing import of CommandNotFoundError from pb_base.handler ...")
        from pb_base.handler import CommandNotFoundError

        log.info("Testing import of pb_base.handler.df ...")
        import pb_base.handler.df

        log.info("Testing import of DfError from pb_base.handler.df ...")
        from pb_base.handler.df import DfError

        log.info("Testing import of DfResult from pb_base.handler.df ...")
        from pb_base.handler.df import DfResult

        log.info("Testing import of DfHandler from pb_base.handler.df ...")
        from pb_base.handler.df import DfHandler

        log.info("Testing import of pb_base.handler.fuser ...")
        import pb_base.handler.fuser

        log.info("Testing import of FuserError from pb_base.handler.fuser ...")
        from pb_base.handler.fuser import FuserError

        log.info("Testing import of FuserHandler from pb_base.handler.fuser ...")
        from pb_base.handler.fuser import FuserHandler

#==============================================================================


if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTest(TestPbBaseHandler('test_import', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
