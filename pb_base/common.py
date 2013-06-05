#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: module for some common used objects and routines
"""

# Standard modules
import sys
import os
import re
import logging
import logging.handlers
import pprint
import platform

# Third party modules

# Own modules

__version__ = '0.3.2'

log = logging.getLogger(__name__)

#==============================================================================
def human2mbytes(value, si_conform = False, as_float = False):
    """
    Converts the given human readable byte value (e.g. 5MB, 8.4GiB etc.)
    with a prefix into an integer/float value (without a prefix) of MiBiBytes.
    It raises a ValueError on invalid values.

    Available prefixes are:
        - kB (1000), KB (1024), KiB (1024)
        - MB (1000*1000), MiB (1024*1024)
        - GB (1000^3), GiB (1024^3)
        - TB (1000^4), TiB (1024^4)
        - PB (1000^5), PiB (1024^5)
        - EB (1000^6), EiB (1024^6)
        - ZB (1000^7), ZiB (1024^7)

    @param value: the value to convert
    @type value: str
    @param si_conform: use factor 1000 instead of 1024 for kB a.s.o.
    @type si_conform: bool
    @param as_float: flag to gives back the value as a float value
                     instead of an integer value
    @type as_float: bool

    @return: amount of MibiBytes
    @rtype:  int or float
    """

    if value is None:
        msg = ("Given value is 'None'.")
        raise ValueError(msg)
    print "Value: '%s'" % (value)

    radix = '.'
    radix = re.escape(radix)

    value_raw = ''
    prefix = None
    pattern = r'^\s*\+?(\d+(?:' + radix + r'\d*)?)\s*(\S+)?'
    match = re.search(pattern, value)
    if match is not None:
        value_raw = match.group(1)
        prefix = match.group(2)
    else:
        msg = ("Could not determine bytes in '%s'.") % (value)
        raise ValueError(msg)

    value_float = float(value_raw)
    if prefix is None:
        prefix = ''

    factor_bin = long(1024)
    factor_si = long(1000)
    if not si_conform:
        factor_si = factor_bin

    factor = long(1)

    if re.search(r'^\s*(?:b(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = long(1)
    elif re.search(r'^\s*k(?:[bB](?:[Yy][Tt][Ee])?)?\s*$', prefix):
        factor = factor_si
    elif re.search(r'^\s*Ki?(?:[bB](?:[Yy][Tt][Ee])?)?\s*$', prefix):
        factor = factor_bin
    elif re.search(r'^\s*M(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si * factor_si)
    elif re.search(r'^\s*MiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin * factor_bin)
    elif re.search(r'^\s*G(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si ** 3)
    elif re.search(r'^\s*GiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin ** 3)
    elif re.search(r'^\s*T(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si ** 4)
    elif re.search(r'^\s*TiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin ** 4)
    elif re.search(r'^\s*P(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si ** 5)
    elif re.search(r'^\s*PiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin ** 5)
    elif re.search(r'^\s*E(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si ** 6)
    elif re.search(r'^\s*EiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin ** 6)
    elif re.search(r'^\s*Z(?:B(?:yte)?)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_si ** 7)
    elif re.search(r'^\s*ZiB(?:yte)?\s*$', prefix, re.IGNORECASE):
        factor = (factor_bin ** 7)
    else:
        msg = ("Couldn't detect prefix '%s'.") % (prefix)
        raise ValueError(msg)

    lbytes = long(factor * value_float)
    mbytes = float(lbytes) / 1024.0 / 1024.0
    if as_float:
        return mbytes
    mbytes = int(mbytes)

    return mbytes

#==============================================================================
def bytes2human(value, si_conform = False, precision = 0):
    """
    Converts the given value in bytes into a human readable format.
    The limit for electing the next higher prefix is at 1500.

    It raises a ValueError on invalid values.

    @param value: the value to convert
    @type value: long
    @param si_conform: use factor 1000 instead of 1024 for kB a.s.o.,
                       if do so, than the units are for example MB instead MiB.
    @type si_conform: bool
    @param precision: how many digits after the decimal point have to stay
                      in the result
    @type precision: int

    @return: the value in a human readable format together with the unit
    @rtype: str

    """

    val = long(value)

    base = 1024
    prefixes = {
        1: 'KiB',
        2: 'MiB',
        3: 'GiB',
        4: 'TiB',
        5: 'PiB',
        6: 'EiB',
        7: 'ZiB',
        8: 'YiB',
    }
    if si_conform:
        base = 1000
        prefixes = {
            1: 'kB',
            2: 'MB',
            3: 'GB',
            4: 'TB',
            5: 'PB',
            6: 'EB',
            7: 'ZB',
            8: 'YB',
        }

    exponent = 0

    float_val = float(val)
    while float_val >= 1500 and exponent < 8:
        float_val /= base
        exponent += 1

    unit = ''
    if exponent:
        unit = ' ' + prefixes[exponent]

    return "%.*f%s" % (precision, float_val, unit)

#==============================================================================
def pp(value):
    """
    Returns a pretty print string of the given value.

    @return: pretty print string
    @rtype: str
    """

    pretty_printer = pprint.PrettyPrinter(indent = 4)
    return pretty_printer.pformat(value)

#==============================================================================
def to_bool(value):
    """
    Converter from string to boolean values (e.g. from configurations)
    """

    if not value:
        return False

    try:
        v_int = int(value)
    except ValueError:
        pass
    else:
        if v_int == 0:
            return False
        else:
            return True

    v_str = ''
    if isinstance(value, basestring):
        if isinstance(value, unicode):
            v_str = value.encode('utf-8')
        else:
            v_str = value
    else:
        v_str = str(value)

    match = re.search(r'^\s*(?:y(?:es)?|true)\s*$', v_str, re.IGNORECASE)
    if match:
        return True

    match = re.search(r'^\s*(?:no?|false|off)\s*$', v_str, re.IGNORECASE)
    if match:
        return False

    return bool(value)

#==============================================================================
def caller_search_path():
    """
    Builds a search path for executables from environment $PATH
    including some standard paths.

    @return: all existing search paths
    @rtype: list
    """

    path_list = []
    search_path = os.environ['PATH']
    if not search_path:
        search_path = os.defpath

    search_path_list = [
        '/opt/profitbricks/bin',
        '/opt/pb/bin',
    ]

    for d in search_path.split(os.pathsep):
        search_path_list.append(d)

    default_path = [
        '/bin',
        '/usr/bin',
        '/usr/local/bin',
        '/sbin',
        '/usr/sbin',
        '/usr/local/sbin',
    ]

    for d in default_path:
        search_path_list.append(d)

    for d in search_path_list:
        if not os.path.exists(d):
            continue
        if not os.path.isdir(d):
            continue
        d_abs = os.path.realpath(d)
        if not d_abs in path_list:
            path_list.append(d_abs)

    return path_list

#==============================================================================
def to_unicode_or_bust(obj, encoding = 'utf-8'):
    """
    Transforms a string, what is not a unicode string, into a unicode string.
    All other objects are left untouched.

    @param obj: the object to transform
    @type obj:  object
    @param encoding: the encoding to use to decode the object,
    @type encoding:  str

    @return: the maybe decoded object
    @rtype:  object

    """

    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)

    return obj

#==============================================================================
def to_utf8_or_bust(obj):
    """
    Transforms a string, what is a unicode string, into a utf-8 encoded string.
    All other objects are left untouched.

    @param obj: the object to transform
    @type obj:  object

    @return: the maybe encoded object
    @rtype:  object

    """

    return encode_or_bust(obj, 'utf-8')

#==============================================================================
def encode_or_bust(obj, encoding = 'utf-8'):
    """
    Encodes the given unicode object into the given encoding.

    @param obj: the object to encode
    @type obj:  object
    @param encoding: the encoding to use to encode the object,
    @type encoding:  str

    @return: the maybe encoded object
    @rtype:  object

    """

    if isinstance(obj, basestring):
        if isinstance(obj, unicode):
            obj = obj.encode(encoding)

    return obj

#==============================================================================
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

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
