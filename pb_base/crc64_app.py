#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2016 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for an application object for the 'crc64' application.
"""

# Standard modules
import logging

# Third party modules

# Own modules
from pb_base.app import PbApplicationError
from pb_base.app import PbApplication

from pb_base.crc import crc64_digest

from pb_base.translate import pb_gettext, pb_ngettext

try:
    import pb_base.local_version as my_version
except ImportError:
    import pb_base.global_version as my_version

__version__ = '0.3.3'

log = logging.getLogger(__name__)

_ = pb_gettext
__ = pb_ngettext


# =============================================================================
class Crc64AppError(PbApplicationError):
    """Base error class for all exceptions happened during
    execution this application"""

    pass


# =============================================================================
class Crc64App(PbApplication):
    """
    Application class for the 'crc64' application.
    """

    # -------------------------------------------------------------------------
    def __init__(
            self, verbose=0, version=my_version.__version__, *arg, **kwargs):
        """
        Initialisation of the crc64 application object.
        """

        indent = ' ' * self.usage_term_len

        usage = "%%(prog)s [%s] TOKEN [TOKEN ...]" % (_('General options'))
        usage += '\n'
        usage += indent + "%(prog)s -h|--help\n"
        usage += indent + "%(prog)s -V|--version"

        desc = _("Generates a 64 bit checksum for all given positional arguments.")

        super(Crc64App, self).__init__(
            usage=usage,
            description=desc,
            verbose=verbose,
            version=version,
            *arg, **kwargs
        )

        self.post_init()
        self.initialized = True

    # -------------------------------------------------------------------------
    def _run(self):
        """The underlaying startpoint of the application."""

        for token in self.args.tokens:
            digest = crc64_digest(token)
            print(digest)

    # -------------------------------------------------------------------------
    def init_arg_parser(self):
        """
        Method to initiate the argument parser.
        """

        super(Crc64App, self).init_arg_parser()

        self.arg_parser.add_argument(
            'tokens',
            metavar='TOKEN',
            type=str,
            nargs='+',
            help=_('The token to generate a CRC64 digest from.'),
        )

# =============================================================================

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
