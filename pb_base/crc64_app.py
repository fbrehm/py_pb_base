#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for an application object for the 'crc64' application.
"""

# Standard modules
import sys
import os
import logging
import re
import time

# Third party modules
import argparse

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.errors import PbError

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError
from pb_base.app import PbApplication

from pb_base.crc import crc64, crc64_digest

from pb_base.translate import translator

__version__ = '0.1.0'

log = logging.getLogger(__name__)

_ = translator.lgettext
__ = translator.lngettext

#==============================================================================
class Crc64AppError(PbApplicationError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass

#==============================================================================
class Crc64App(PbApplication):
    """
    Application class for the 'crc64' application.
    """

    #--------------------------------------------------------------------------
    def __init__(self,
            verbose = 0,
            version = __version__,
            *arg, **kwargs):
        """
        Initialisation of the crc64 application object.
        """

        indent = ' ' * self.usage_term_len

        usage = "%%(prog)s [%s] TOKEN [TOKEN ...]" % (_('general options'))
        usage += '\n'
        usage += indent + "%(prog)s -h|--help\n"
        usage += indent + "%(prog)s -V|--version"

        super(Crc64App, self).__init__(
                usage = usage,
                verbose = verbose,
                version = version,
                *arg, **kwargs
        )

        self.post_init()
        self.initialized = True

    #--------------------------------------------------------------------------
    def _run(self):
        """The underlaying startpoint of the application."""

        log.debug("Starting ...")
        log.info("Doing some strange things ...")
        time.sleep(1)
        log.debug("Ending ...")

    #--------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.
        """

        super(Crc64App, self).init_arg_parser()

        self.arg_parser.add_argument(
                'tokens',
                metavar = 'TOKEN',
                type = str,
                nargs = '+',
                help = _('The tokens to generate CRC64 digests from.'),
        )




#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
