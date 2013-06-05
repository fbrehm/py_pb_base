#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: All modules for Python base object and error classes
"""

import os
import sys
import re
import platform

__author__ = 'Frank Brehm <frank.brehm@profitbricks.com>'
__copyright__ = '(C) 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin'
__contact__ = 'frank.brehm@profitbricks.com'
__version__ = '0.4.9'
__license__ = 'LGPLv3+'

#--------------------------------------------------------------------------
def terminal_can_colors(debug = False):
    """
    Method to detect, whether the current terminal (stdout and stderr)
    is able to perform ANSI color sequences.

    @return: both stdout and stderr can perform ANSI color sequences
    @rtype: bool

    """

    cur_term = ''
    if 'TERM' in os.environ:
        cur_term = os.environ['TERM'].lower().strip()

    colored_term_list = (
        r'ansi',
        r'linux.*',
        r'screen.*',
        r'[xeak]term.*',
        r'gnome.*',
        r'rxvt.*',
        r'interix',
    )
    term_pattern = r'^(?:' + r'|'.join(colored_term_list) + r')$'
    re_term = re.compile(term_pattern)

    ansi_term = False
    env_term_has_colors = False

    if cur_term:
        if cur_term == 'ansi':
            env_term_has_colors = True
            ansi_term = True
        elif re_term.search(cur_term):
            env_term_has_colors = True
    if debug:
        sys.stderr.write("ansi_term: %r, env_term_has_colors: %r\n" % (
                ansi_term, env_term_has_colors))

    has_colors = False
    if env_term_has_colors:
        has_colors = True
    for handle in [sys.stdout, sys.stderr]:
        if (hasattr(handle, "isatty") and handle.isatty()):
            if debug:
                sys.stderr.write("%s is a tty.\n" % (handle.name))
            if (platform.system() == 'Windows' and not ansi_term):
                if debug:
                    sys.stderr.write("platform is Windows and not ansi_term.\n")
                has_colors = False
        else:
            if debug:
                sys.stderr.write("%s is not a tty.\n" % (handle.name))
            if ansi_term:
                pass
            else:
                has_colors = False

    return has_colors

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
