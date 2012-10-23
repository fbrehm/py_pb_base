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

import pb_base.pidfile

from pb_base.pidfile import PidFileError
from pb_base.pidfile import PidFile

# Some predefined module variables / constants
pidfile_normal = 'test_pidfile.pid'

#==============================================================================

class TestPidFile(unittest.TestCase):

    #--------------------------------------------------------------------------
    def setUp(self):
        pass

    #--------------------------------------------------------------------------
    def test_object(self):

        try:
            pid_file = PidFile(
                filename = pidfile_normal,
                appname = 'test_pidfile',
                verbose = 1,
            )
            print "\nPidFile object:\n%s" % (pid_file)

        except Exception, e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))

    #--------------------------------------------------------------------------
    def test_no_filename(self):

        try:
            pid_file = PidFile(
                filename = '',
                appname = 'test_pidfile',
                verbose = 1,
            )

        except ValueError, e:
            pass
        except Exception, e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))
        else:
            self.fail("No ValueError raised on a wrong filename ''.")

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
            'test_pidfile.TestPidFile.test_object'))
    suite.addTests(loader.loadTestsFromName(
            'test_pidfile.TestPidFile.test_no_filename'))

    runner = unittest.TextTestRunner(verbosity = args.verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
