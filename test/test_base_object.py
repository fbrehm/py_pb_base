#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@organization: Profitbricks GmbH
@copyright: (c) 2010-2012 by Profitbricks GmbH
@license: GPL3
@summary: test script (and module) for unit tests on base object
'''

import unittest
import os
import sys

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import pb_base.object

from pb_base.object import PbBaseObjectError
from pb_base.object import PbBaseObject

#==============================================================================

class TestPbBaseObject(unittest.TestCase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_object(self):

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = 1,
            )
            print "\nBase object: %r" % (obj.__dict__)

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_verbose1(self):

        v = 'hh'

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = v,
            )

        except ValueError, e:
            pass
        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))
        else:
            self.fail("No ValueError raised on a wrong verbose level %r." % (v))

    #--------------------------------------------------------------------------
    def test_verbose2(self):

        v = -2

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = v,
            )

        except ValueError, e:
            pass
        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))
        else:
            self.fail("No ValueError raised on a wrong verbose level %r." % (v))

    #--------------------------------------------------------------------------
    def test_basedir1(self):

        bd = '/blablub'

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                base_dir = bd,
            )

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_basedir2(self):

        bd = '/etc/passwd'

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                base_dir = bd,
            )

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_as_dict1(self):

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = 1,
            )

            di = obj.as_dict()
            if isinstance(di, dict):
                print "Got PbBaseObject.as_dict(): %r" %(di)
            else:
                self.fail("Wrong result from PbBaseObject.as_dict(): %r" %(di))

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_as_dict2(self):

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = 1,
            )

            obj.obj2 = PbBaseObject(
                appname = 'test_base_object2',
                verbose = 1,
            )

            di = obj.as_dict()
            if isinstance(di, dict):
                print "Got PbBaseObject.as_dict(): %r" %(di)
            else:
                self.fail("Wrong result from PbBaseObject.as_dict(): %r" %(di))

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_as_dict3(self):

        try:
            obj = PbBaseObject(
                appname = 'test_base_object',
                verbose = 1,
            )

            obj.obj2 = PbBaseObject(
                appname = 'test_base_object2',
                verbose = 1,
            )

            out = str(obj)
            print "Got str(PbBaseObject): %s" %(out)

        except Exception, e:
            self.fail("Could not instatiate PbBaseObject by a %s: %s" % (
                    e.__class__.__name__, str(e)))

#==============================================================================

if __name__ == '__main__':

    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-v", "--verbose", action = "count",
            dest = 'verbose', help = 'Increase the verbosity level')
    args = arg_parser.parse_args()

    unittest.main(verbosity = args.verbose)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
