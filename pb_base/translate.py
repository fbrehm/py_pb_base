#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2016 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module for i18n.
          It provides translation object, usable from all other
          modules in this package.
"""

# Standard modules
import os
import logging
import gettext

# Third party modules
import six

# Own modules
from pb_base.common import to_str_or_bust

log = logging.getLogger(__name__)

basedir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
locale_dir = os.path.join(basedir, 'po')
if not os.path.isdir(locale_dir):
    locale_dir = None

DOMAIN = 'py_pb_base'

mo_file = gettext.find(DOMAIN, locale_dir)

translator = gettext.translation(DOMAIN, locale_dir, fallback=True)
"""
The main gettext-translator object, which can be imported
from other modules.
"""


# =============================================================================
def pb_gettext(message):
    if six.PY3:
        return to_str_or_bust(translator.gettext(message))
    else:
        return to_str_or_bust(translator.lgettext(message))


# =============================================================================
def pb_ngettext(singular, plural, n):
    if six.PY3:
        return to_str_or_bust(translator.ngettext(singular, plural, n))
    else:
        return to_str_or_bust(translator.lngettext(singular, plural, n))

_ = pb_gettext

# =============================================================================

if __name__ == "__main__":

    print(_("Basedir: %r") % (basedir))
    print(_("Locales dir: %r") % (locale_dir))
    print(_("Domain: %r") % (DOMAIN))
    print(_("Found .mo-file: %r") % (mo_file))

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
