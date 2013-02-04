#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, ProfitBricks GmbH, Berlin
@summary: module for some common used functions for generating
          of hashed password suitable for /etc/shadow
"""

# Standard modules
import re
import crypt
import random

valid_hash_algos = {
    None:       None,
    1:          1,
    5:          5,
    6:          6,
    '1':        1,
    '5':        5,
    '6':        6,
    'crypt':    None,
    'md5':      1,
    'sha256':   5,
    'sha512':   6,
}

#==============================================================================
def gensalt(length = 8):
    """
    Generating a salt, a string of randomly generated characters from the range
    of the decimal numbers, uppercase and lowercase letters, the dot ('.')
    character and the slash character ('/').

    @raise ValueError: if an invalid length was given

    @param length: the length of the salt to generate (mostly 2 or 8,
                   must be greater than 0)
    @type length: int

    @return: the generated salt
    @rtype: str

    """

    length = int(length)
    if length <= 0:
        msg = "An invalid length of %d was given, must be greater than 0." % (
                length)
        raise ValueError(msg)

    chars = map(lambda x: chr(x), range(46, 57) + range(65, 90) + range(97, 122))
    salt=[]
    for i in range(length):
        salt.append(random.choice(chars))

    return "".join(salt)

#==============================================================================
def shadowcrypt(password, hashalgo = 'sha512', saltlen = None, salt = None):
    """
    Crypt the given password with the given hashing algorithm and salt in a
    format, suitable for /etc/shadow.

    @raise ValueError: if an invalid hashing algorithm and/or length of salt
                       was given

    @param password: the password to crypt
    @type password: str
    @param hashalgo: the hashing algorithm to use for crypting. Usable
                     algorithms are: 'crypt', 'md5', 'sha256' and 'sha512'.
    @type hashalgo: str
    @param saltlen: the length of the salt to generate, if no salt is given.
                    Must be greater than 0.
    @type saltlen: int
    @param salt: The salt to use to encrypt the password. If not given,
                 a new one will be generated.
    @type salt: str

    @return: the crypted/hashed password
    @rtype: str

    """

    if not hashalgo in valid_hash_algos:
        msg = "Invalid hashing algorithm %r given." % (hashalgo)
        raise ValueError(msg)

    algo = valid_hash_algos[hashalgo]

    if not salt:
        salt = gensalt(saltlen)

    salt2use = salt
    if algo:
        if not re.search(r'^\$[156]\$[0-9a-z\.\/]+\$', salt, re.IGNORECASE):
            salt2use = '$%d$%s$' % (algo, salt)

    return crypt.crypt(password, salt2use)

#==============================================================================

if __name__ == "__main__":
    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
