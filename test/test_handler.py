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
        self.appname = 'test_handler'

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

        log.info("Testing import of PbBaseHandler from pb_base.handler ...")
        from pb_base.handler import PbBaseHandler

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

    #--------------------------------------------------------------------------
    def test_command_not_found_error(self):

        log.info("Test raising a CommandNotFoundError exception ...")

        from pb_base.handler import CommandNotFoundError

        with self.assertRaises(CommandNotFoundError) as cm:
            raise CommandNotFoundError('uhu')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

        with self.assertRaises(CommandNotFoundError) as cm:
            raise CommandNotFoundError(['uhu'])
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

        with self.assertRaises(CommandNotFoundError) as cm:
            raise CommandNotFoundError(['uhu', 'bla'])
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

        with self.assertRaises(TypeError) as cm:
            raise CommandNotFoundError()
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

        with self.assertRaises(TypeError) as cm:
            raise CommandNotFoundError('uhu', 'bla')
        e = cm.exception
        log.debug("%s raised: %s", e.__class__.__name__, e)

    #--------------------------------------------------------------------------
    def test_generic_handler_object(self):

        log.info("Testing init of a generic handler object.")

        from pb_base.handler import PbBaseHandler

        hdlr = PbBaseHandler(
            appname = self.appname,
            verbose = self.verbose,
        )
        log.debug("PbBaseHandler %%r: %r", hdlr)
        log.debug("PbBaseHandler %%s: %s", str(hdlr))

    #--------------------------------------------------------------------------
    def test_df_handler_object(self):

        log.info("Testing init of a df handler object.")

        from pb_base.handler.df import DfHandler

        df = DfHandler(
            appname = self.appname,
            verbose = self.verbose,
        )
        log.debug("DfHandler %%r: %r", df)
        log.debug("DfHandler %%s: %s", str(df))

    #--------------------------------------------------------------------------
    def test_fuser_handler_object(self):

        log.info("Testing init of a fuser handler object.")

        from pb_base.handler.fuser import FuserHandler

        fuser = FuserHandler(
            appname = self.appname,
            verbose = self.verbose,
        )
        log.debug("FuserHandler %%r: %r", fuser)
        log.debug("FuserHandler %%s: %s", str(fuser))

    #--------------------------------------------------------------------------
    def test_exec_df_root(self):

        log.info("Testing execution of df on the root filesystem.")

        from pb_base.handler.df import DfHandler

        df = DfHandler(
            appname = self.appname,
            verbose = self.verbose,
        )

        result = df('/')
        res = []
        for r in result:
            res.append(r.as_dict())
        log.debug("Got a result from 'df /':\n%s", pp(res))

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
    suite.addTest(TestPbBaseHandler('test_command_not_found_error', verbose))
    suite.addTest(TestPbBaseHandler('test_generic_handler_object', verbose))
    suite.addTest(TestPbBaseHandler('test_df_handler_object', verbose))
    suite.addTest(TestPbBaseHandler('test_fuser_handler_object', verbose))
    suite.addTest(TestPbBaseHandler('test_exec_df_root', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
