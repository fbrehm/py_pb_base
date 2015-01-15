#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: © 2010 - 2015 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on base object
'''

import os
import sys
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import general
from general import PbBaseTestcase, get_arg_verbose, init_root_logger

log = logging.getLogger('test_base_object')


# =============================================================================
class TestPbBaseObject(PbBaseTestcase):

    # -------------------------------------------------------------------------
    def setUp(self):
        pass

    # -------------------------------------------------------------------------
    def test_import(self):

        log.info("Testing import of pb_base.object ...")
        import pb_base.object

    # -------------------------------------------------------------------------
    def test_object(self):

        log.info("Testing init of a simple object.")

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(
            appname='test_base_object',
            verbose=1,
        )
        log.debug("PbBaseObject %%r: %r", obj)
        log.debug("PbBaseObject %%s: %s", str(obj))

    # -------------------------------------------------------------------------
    def test_verbose1(self):

        log.info("Testing wrong verbose values #1.")

        import pb_base.object
        from pb_base.object import PbBaseObject

        v = 'hh'
        obj = None

        with self.assertRaises(ValueError) as cm:
            obj = PbBaseObject(appname='test_base_object', verbose=v)
        e = cm.exception
        log.debug("ValueError raised on verbose = %r: %s", v, str(e))

    # -------------------------------------------------------------------------
    def test_verbose2(self):

        log.info("Testing wrong verbose values #2.")

        import pb_base.object
        from pb_base.object import PbBaseObject

        v = -2
        obj = None

        with self.assertRaises(ValueError) as cm:
            obj = PbBaseObject(appname='test_base_object', verbose=v)
        e = cm.exception
        log.debug("ValueError raised on verbose = %r: %s", v, str(e))

    # -------------------------------------------------------------------------
    def test_basedir1(self):

        bd = '/blablub'
        log.info("Testing #1 wrong basedir: %r", bd)

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', base_dir=bd)

    # -------------------------------------------------------------------------
    def test_basedir2(self):

        bd = '/etc/passwd'
        log.info("Testing #2 wrong basedir: %r", bd)

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', base_dir=bd)

    # -------------------------------------------------------------------------
    def test_as_dict1(self):

        log.info("Testing obj.as_dict() #1 - simple")

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', verbose=1)

        di = obj.as_dict()
        log.debug("Got PbBaseObject.as_dict(): %r", di)
        self.assertIsInstance(di, dict)

    # -------------------------------------------------------------------------
    def test_as_dict2(self):

        log.info("Testing obj.as_dict() #2 - stacked")

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', verbose=1)
        obj.obj2 = PbBaseObject(appname='test_base_object2', verbose=1)

        di = obj.as_dict()
        log.debug("Got PbBaseObject.as_dict(): %r", di)
        self.assertIsInstance(di, dict)
        self.assertIsInstance(obj.obj2.as_dict(), dict)

    # -------------------------------------------------------------------------
    def test_as_dict3(self):

        log.info("Testing obj.as_dict() #3 - typecasting to str")

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', verbose=1)
        obj.obj2 = PbBaseObject(appname='test_base_object2', verbose=1)

        out = str(obj)
        self.assertIsInstance(out, str)
        log.debug("Got str(PbBaseObject): %s", out)

    # -------------------------------------------------------------------------
    def test_as_dict_short(self):

        log.info("Testing obj.as_dict() #4 - stacked and short")

        import pb_base.object
        from pb_base.object import PbBaseObject

        obj = PbBaseObject(appname='test_base_object', verbose=1)
        obj.obj2 = PbBaseObject(appname='test_base_object2', verbose=1)

        di = obj.as_dict(short=True)
        log.debug("Got PbBaseObject.as_dict(): %r", di)
        self.assertIsInstance(di, dict)
        self.assertIsInstance(obj.obj2.as_dict(), dict)

# =============================================================================

if __name__ == '__main__':

    verbose = get_arg_verbose()
    if verbose is None:
        verbose = 0
    init_root_logger(verbose)

    log.info("Starting tests ...")

    suite = unittest.TestSuite()

    suite.addTest(TestPbBaseObject('test_import', verbose))
    suite.addTest(TestPbBaseObject('test_object', verbose))
    suite.addTest(TestPbBaseObject('test_verbose1', verbose))
    suite.addTest(TestPbBaseObject('test_verbose2', verbose))
    suite.addTest(TestPbBaseObject('test_basedir1', verbose))
    suite.addTest(TestPbBaseObject('test_basedir2', verbose))
    suite.addTest(TestPbBaseObject('test_as_dict1', verbose))
    suite.addTest(TestPbBaseObject('test_as_dict2', verbose))
    suite.addTest(TestPbBaseObject('test_as_dict3', verbose))
    suite.addTest(TestPbBaseObject('test_as_dict_short', verbose))

    runner = unittest.TextTestRunner(verbosity=verbose)

    result = runner.run(suite)


# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
