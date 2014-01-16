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
import locale

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust
from pb_base.common import bytes2human

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

locale.setlocale(locale.LC_ALL, '')

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
    def format_df_results(self, result_list, human = False):

        gr = locale.localeconv()['grouping']
        res_list = []
        for result in result_list:
            df_entry = {}
            df_entry['dev'] = result.dev
            df_entry['fs'] = result.fs
            df_entry['type'] = result.fs_type
            df_entry['total'] = locale.format("%d", result.total_mb, gr)
            df_entry['used'] = locale.format("%d", result.used_mb, gr)
            df_entry['free'] = locale.format("%d", result.free_mb, gr)
            if result.used_percent is None:
                df_entry['used_pc'] = "-"
            else:
                df_entry['used_pc'] = locale.format("%.2f",
                        result.used_percent) + " %"
            if human:
                df_entry['total'] = bytes2human(result.total_mb)
                df_entry['used'] = bytes2human(result.used_mb)
                df_entry['free'] = bytes2human(result.free_mb)

            res_list.append(df_entry)

        if self.verbose > 2:
            log.debug("Formatted DF results: %s", pp(res_list))

        keys = ('dev', 'type', 'total', 'used', 'free', 'used_pc')
        length = {}
        for key in keys:
            length[key] = 1

        cur_locale = locale.getlocale()
        cur_encoding = cur_locale[1]
        if (cur_locale[1] is None or cur_locale[1] == '' or
                cur_locale[1].upper() == 'C' or
                cur_locale[1].upper() == 'POSIX'):
            cur_encoding = 'UTF-8'

        for result in res_list:

            for key in keys:
                tt = result[key]
                if sys.version_info[0] <= 2:
                    tt = tt.decode(cur_encoding)
                if len(tt) > length[key]:
                    length[key] = len(tt)

        out = ''
        for result in res_list:
            line = "%-*s  %-*s  %*s  %*s  %*s  %*s  %s\n" % (
                    length['dev'], result['dev'],
                    length['type'], result['type'],
                    length['total'], result['total'],
                    length['used'], result['used'],
                    length['free'], result['free'],
                    length['used_pc'], result['used_pc'],
                    result['fs'],
            )
            out += line

        if self.verbose > 2:
            log.debug("Field lengths: %s", pp(length))

        return out

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
        if self.verbose > 2:
            res = []
            for r in result:
                res.append(r.as_dict())
            log.debug("Got a result from 'df /':\n%s", pp(res))

        out = self.format_df_results(result).strip()
        log.debug("DF of root filesystem:\n%s", out)

    #--------------------------------------------------------------------------
    def test_exec_df_all(self):

        log.info("Testing execution of df on all filesystems.")

        from pb_base.handler.df import DfHandler

        df = DfHandler(
            appname = self.appname,
            verbose = self.verbose,
        )

        result = df(all_fs = True)
        if self.verbose > 2:
            res = []
            for r in result:
                res.append(r.as_dict())
            log.debug("Got a result for all 'df':\n%s", pp(res))

        out = self.format_df_results(result).strip()
        log.debug("DF of all filesystems:\n%s", out)

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
    suite.addTest(TestPbBaseHandler('test_exec_df_all', verbose))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
