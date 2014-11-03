#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: The module is for additional check functions used by validate.Validator
"""

# Standard modules
import sys

# Third party modules
from validate import Validator
from validate import ValidateError
from validate import VdtMissingValue
from validate import VdtUnknownCheckError
from validate import VdtParamError
from validate import VdtTypeError
from validate import VdtValueError
from validate import VdtValueTooSmallError
from validate import VdtValueTooBigError
from validate import VdtValueTooShortError
from validate import VdtValueTooLongError


# -----------------------------------------------------------------------------
def oct_check(value, min_val=None, max_val=None):
    """
    Check, that the supplied value is an octal integer value.
    """

    maxv = None
    minv = None

    if min_val is not None:
        if not isinstance(min_val, (int, str)):
            raise VdtParamError('min_val', min_val)
        if isinstance(min_val, str):
            minv = min_val.strip()
            if minv.startswith('0x') or minv.startswith('0X'):
                minv = minv[2:]
                try:
                    minv = int(minv, 16)
                except ValueError:
                    raise VdtParamError('min_val', min_val)
            elif minv.startswith('0'):
                try:
                    minv = int(minv, 8)
                except ValueError:
                    raise VdtParamError('min_val', min_val)
            else:
                try:
                    minv = int(minv)
                except ValueError:
                    raise VdtParamError('min_val', min_val)

    if max_val is not None:
        if not isinstance(max_val, (int, str)):
            raise VdtParamError('max_val', max_val)
        if isinstance(max_val, str):
            maxv = max_val.strip()
            if maxv.startswith('0x') or maxv.startswith('0X'):
                maxv = maxv[2:]
                try:
                    maxv = int(maxv, 16)
                except ValueError:
                    raise VdtParamError('max_val', max_val)
            elif maxv.startswith('0'):
                try:
                    maxv = int(maxv, 8)
                except ValueError:
                    raise VdtParamError('max_val', max_val)
            else:
                try:
                    maxv = int(maxv)
                except ValueError:
                    raise VdtParamError('max_val', max_val)

    if not isinstance(value, str):
        raise VdtTypeError(value)

    try:
        v = int(value, 8)
    except ValueError:
        raise VdtTypeError(value)

    if (minv is not None) and (v < minv):
        raise VdtValueTooSmallError(value)
    if (maxv is not None) and (v > maxv):
        raise VdtValueTooBigError(value)
    if v < 0:
        return "-0%o" % (v)
    if v == 0:
        return "0"
    return "0%o" % (v)

# =============================================================================

pbvalidator_checks = {
    'oct': oct_check,
}

# -----------------------------------------------------------------------------

if __name__ == "__main__":

    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
