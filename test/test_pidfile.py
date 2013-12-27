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
import time
import re

libdir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, libdir)

import pb_base.pidfile

from pb_base.pidfile import PidFileError
from pb_base.pidfile import InvalidPidFileError
from pb_base.pidfile import PidFileInUseError
from pb_base.pidfile import PidFile

# Some predefined module variables / constants
pidfile_normal = 'test_pidfile.pid'
pidfile_forbidden = '/root/test_pidfile.pid'
pidfile_invalid = '/bla/blub/blubber.pid'

#==============================================================================
def file_content(filename):

    if not os.path.isfile(filename):
        sys.stderr.write("File '%s' doesn't exists.\n" % (filename))
        return None

    fh = None
    content = None
    try:
        fh = open(filename)
        content = ''.join(fh.readlines())
    except IOError as e:
        sys.stderr.write("Could not read file '%s': %s\n" % (filename, str(e)))
    finally:
        if fh:
            fh.close()

    return content

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
            print("\nPidFile object:\n%s" % (pid_file))

        except Exception as e:
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

        except ValueError as e:
            sys.stderr.write("%s: %r " % (e.__class__.__name__, str(e)))
        except Exception as e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))
        else:
            self.fail("No ValueError raised on a wrong filename ''.")

    #--------------------------------------------------------------------------
    def test_create_normal(self):

        pid_file = None

        try:
            pid_file = PidFile(
                filename = pidfile_normal,
                appname = 'test_pidfile',
                verbose = 3,
            )

        except Exception as e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))

        try:
            pid_file.create()
            if not pid_file.created:
                self.fail("Pidfile '%s' seems not to be created.",
                        pidfile_normal)
            if not os.path.exists(pidfile_normal):
                self.fail("Pidfile '%s' not created.", pidfile_normal)
            fcontent = file_content(pidfile_normal)
            if fcontent is None:
                self.fail("Could not read pidfile '%s'.", pidfile_normal)
            elif not fcontent:
                self.fail("Pidfile '%s' seems to be empty.", pidfile_normal)
            else:
                match = re.search(r'^\s*(\d+)\s*$', fcontent)
                if not match:
                    self.fail("Pidfile '%s' with invalid content: %r",
                            pidfile_normal, fcontent)
                else:
                    pid = int(match.group(1))
                    if pid == os.getpid():
                        sys.stderr.write("Found correct PID %d in '%s'. " % (
                                pid, pidfile_normal))
                    else:
                        self.fail("Found invalid PID %d in '%s', but should be %d.",
                                pid, pidfile_normal, os.getpid())
        finally:
            del pid_file

    #--------------------------------------------------------------------------
    def test_create_forbidden(self):

        pid_file = None

        try:
            pid_file = PidFile(
                filename = pidfile_forbidden,
                appname = 'test_pidfile',
                verbose = 3,
            )

        except Exception as e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))

        try:
            pid_file.create()
        except InvalidPidFileError as e:
            sys.stderr.write("%s: %r " % (e.__class__.__name__, str(e)))
        else:
            if os.geteuid():
                self.fail(("No InvalidPidFileError raised on a forbidden " +
                        "pidfile path '%s' (except for root).") % (
                        pidfile_forbidden))
            else:
                print(("No InvalidPidFileError raised on a forbidden " +
                        "pidfile path '%s', because I'm root.") % (
                        pidfile_forbidden))
        finally:
            del pid_file

    #--------------------------------------------------------------------------
    def test_create_invalid(self):

        pid_file = None

        try:
            pid_file = PidFile(
                filename = pidfile_invalid,
                appname = 'test_pidfile',
                verbose = 3,
            )

        except Exception as e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))

        try:
            pid_file.create()
        except InvalidPidFileError as e:
            sys.stderr.write("%s: %r " % (e.__class__.__name__, str(e)))
        else:
            self.fail(("No InvalidPidFileError raised on a invalid " +
                    "pidfile path '%s'.") % (
                    pidfile_invalid))
        finally:
            del pid_file

    #--------------------------------------------------------------------------
    def test_create_concurrent(self):

        pid_file1 = None
        pid_file2 = None
        carry_on = True

        try:
            pid_file1 = PidFile(
                filename = pidfile_normal,
                appname = 'test_pidfile',
                verbose = 3,
            )
            pid_file2 = PidFile(
                filename = pidfile_normal,
                appname = 'test_pidfile',
                verbose = 3,
            )

        except Exception as e:
            self.fail("Could not instatiate PidFile by a %s: %s" % (
                    e.__class__.__name__, str(e)))
            return

        try:
            pid_file1.create()
        except Exception as e:
            del pid_file1
            del pid_file2
            self.fail("Could not create pidfile '%s' by a %s: %s" % (
                    pidfile_normal, e.__class__.__name__, str(e)))
            return

        try:
            pid_file2.create()
        except PidFileInUseError as e:
            sys.stderr.write("%s: %r " % (e.__class__.__name__, str(e)))
        except Exception as e:
            self.fail("Could not create pidfile '%s' by a %s: %s" % (
                    pidfile_normal, e.__class__.__name__, str(e)))
        finally:
            del pid_file1
            del pid_file2

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
    suite.addTests(loader.loadTestsFromName(
            'test_pidfile.TestPidFile.test_create_normal'))
    suite.addTests(loader.loadTestsFromName(
            'test_pidfile.TestPidFile.test_create_forbidden'))
    suite.addTests(loader.loadTestsFromName(
            'test_pidfile.TestPidFile.test_create_invalid'))
    suite.addTests(loader.loadTestsFromName(
            'test_pidfile.TestPidFile.test_create_concurrent'))

    runner = unittest.TextTestRunner(verbosity = args.verbose)

    result = runner.run(suite)

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
