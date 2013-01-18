#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2013 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on base object
'''

import unittest
import os
import sys
import logging

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

import pb_base.object

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

log = logging.getLogger(__name__)

#==============================================================================

class TestPbBaseObject(PbBaseTestcase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_object(self):

        log.info("Testing init of a simple object.")
        obj = PbBaseObject(
            appname = 'test_base_object',
            verbose = 1,
        )
        log.debug("PbBaseObject %%r: %r", obj)
        log.debug("PbBaseObject %%s: %s", str(obj))

    #--------------------------------------------------------------------------
    def test_verbose1(self):

        log.info("Testing wrong verbose values #1.")
        v = 'hh'
        obj = None

        with self.assertRaises(ValueError) as cm:
            obj = PbBaseObject(appname = 'test_base_object', verbose = v)
        e = cm.exception
        log.debug("ValueError raised on verbose = %r: %s", v, str(e))

    #--------------------------------------------------------------------------
    def test_verbose2(self):

        log.info("Testing wrong verbose values #2.")
        v = -2
        obj = None

        with self.assertRaises(ValueError) as cm:
            obj = PbBaseObject(appname = 'test_base_object', verbose = v)
        e = cm.exception
        log.debug("ValueError raised on verbose = %r: %s", v, str(e))

    #--------------------------------------------------------------------------
    def test_basedir1(self):

        bd = '/blablub'
        log.info("Testing #1 wrong basedir: %r", bd)

        obj = PbBaseObject(appname = 'test_base_object', base_dir = bd)

    #--------------------------------------------------------------------------
    def test_basedir2(self):

        bd = '/etc/passwd'
        log.info("Testing #2 wrong basedir: %r", bd)

        obj = PbBaseObject(appname = 'test_base_object', base_dir = bd)

    #--------------------------------------------------------------------------
    def test_as_dict1(self):

        log.info("Testing obj.as_dict() #1 - simple")

        obj = PbBaseObject(appname = 'test_base_object', verbose = 1)

        di = obj.as_dict()
        log.debug("Got PbBaseObject.as_dict(): %r", di)
        self.assertIsInstance(di, dict)

    #--------------------------------------------------------------------------
    def test_as_dict2(self):

        log.info("Testing obj.as_dict() #2 - stacked")

        obj = PbBaseObject(appname = 'test_base_object', verbose = 1)
        obj.obj2 = PbBaseObject(appname = 'test_base_object2', verbose = 1)

        di = obj.as_dict()
        log.debug("Got PbBaseObject.as_dict(): %r", di)
        self.assertIsInstance(di, dict)
        self.assertIsInstance(obj.obj2.as_dict(), dict)

    #--------------------------------------------------------------------------
    def test_as_dict3(self):

        log.info("Testing obj.as_dict() #3 - typecasting to str")

        obj = PbBaseObject(appname = 'test_base_object', verbose = 1)
        obj.obj2 = PbBaseObject(appname = 'test_base_object2', verbose = 1)

        out = str(obj)
        self.assertIsInstance(out, basestring)
        log.debug("Got str(PbBaseObject): %s", out)

#==============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    init_root_logger(verbose)

    log.info("Starting tests ...")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_object'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_verbose1'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_verbose2'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_basedir1'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_basedir2'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_as_dict1'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_as_dict2'))
    suite.addTests(loader.loadTestsFromName(
            'test_base_object.TestPbBaseObject.test_as_dict3'))

    runner = unittest.TextTestRunner(verbosity = verbose)

    result = runner.run(suite)


#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
