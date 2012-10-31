#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@summary: The module for a daemon application object, which is forking
          to execute the underlaying action.
          It provides all from the daemon application object with
          additional methods and properties for forking.
"""

# Standard modules
import sys
import os
import logging

from gettext import gettext as _

# Third party modules

# Own modules
from pb_base.common import pp, to_unicode_or_bust, to_utf8_or_bust

from pb_base.errors import PbError
from pb_base.errors import FunctionNotImplementedError

import pb_logging
from pb_logging import valid_syslog_facility
from pb_logging.syslog_handler import PbSysLogHandler

from pb_base.object import PbBaseObjectError

from pb_base.app import PbApplicationError

from pb_base.cfg_app import PbCfgAppError

from pb_base.pidfile import PidFileError
from pb_base.pidfile import InvalidPidFileError
from pb_base.pidfile import PidFileInUseError

from pb_base.pidfile_app import PidfileAppError

from pb_base.daemon import PbDaemonError
from pb_base.daemon import PbDaemon

__version__ = '0.1.0'

log = logging.getLogger(__name__)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
