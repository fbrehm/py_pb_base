#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2016 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: module for some common used checksum functions
"""
from functools import reduce

# Standard modules

__version__ = '0.2.1'

# -----------------------------------------------------------------------------
# Module variables

# module variables for crc64
# will initialised in first using of crc64()
POLY64REVh = 0xd8000000
CRCTableh = [0] * 256
CRCTablel = [0] * 256
crc64_initialised = False


# =============================================================================
def crc64(aString):
    """
    Generates a CRC64 checksum from the given string.

    FIXME: what if the string is an unicode string?

    @param aString: the string to generate the checksum
    @type aString: str

    @return: the high and the low part of the 64bit checksum
    @rtype: tuple of two int

    """

    global crc64_initialised
    crcl = 0
    crch = 0

    # init module variables, if necessary
    if not crc64_initialised:

        for i in range(256):
            partl = i
            parth = 0

            for j in range(8):
                rflag = partl & 1
                partl >>= 1
                if (parth & 1):
                    partl |= (1 << 31)
                parth >>= 1
                if rflag:
                    parth ^= POLY64REVh
            CRCTableh[i] = parth
            CRCTablel[i] = partl

        crc64_initialised = True

    # compute the checksum
    for item in aString:
        shr = 0
        shr = (crch & 0xFF) << 24
        temp1h = crch >> 8
        temp1l = (crcl >> 8) | shr
        tableindex = (crcl ^ ord(item)) & 0xFF

        crch = temp1h ^ CRCTableh[tableindex]
        crcl = temp1l ^ CRCTablel[tableindex]

    return (crch, crcl)


# =============================================================================
def crc64_digest(aString):
    """
    Returns a hexidecimal digest from the 64bit checksum
    of the given string.

    @param aString: the string to generate the checksum
    @type aString: str

    @return: hexadecimal digest (16 hexadecimal numbers)
    @rtype: str

    """

    return "%08x%08x" % (crc64(aString))


# =============================================================================
def checksum(string):
    """
    A simple checksum algorithm of a given string.

    Taken from:
    U{http://code.activestate.com/recipes/52251-simple-string-checksum/}

    @param string: the string to build the checksum from
    @type string: str

    @return: the checksum
    @rtype: int
    """

    return reduce(lambda x, y: x + y, list(map(ord, string)))


# =============================================================================
def checksum256(string):
    """
    A simple checksum algorithm of a given string. It's similar
    to checksum(), but gives back the modulo to 256 of the checksum.

    Taken from:
    U{http://code.activestate.com/recipes/52251-simple-string-checksum/}

    @param string: the string to build the checksum from
    @type string: str

    @return: the modulo to 256 of the checksum
    @rtype: int
    """

    return reduce(lambda x, y: x + y, list(map(ord, string))) % 256


# =============================================================================

if __name__ == "__main__":
    pass

# =============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
