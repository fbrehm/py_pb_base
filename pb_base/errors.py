#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@summary: module for some common used error classes
'''

# Standard modules
import errno

__version__ = '0.1.1'


#==============================================================================
class PbError(Exception):
    """
    Base error class for all other self defined exceptions.
    """

#==============================================================================
class FunctionNotImplementedError(PbError, NotImplementedError):
    """
    Error class for not implemented functions.
    """

    #--------------------------------------------------------------------------
    def __init__(self, function_name, class_name):
        """
        Constructor.

        @param function_name: the name of the not implemented function
        @type function_name: str
        @param class_name: the name of the class of the function
        @type class_name: str

        """

        self.function_name = function_name
        if not function_name:
            self.function_name = '__unkown_function__'

        self.class_name = class_name
        if not class_name:
            self.class_name = '__unkown_class__'

    #--------------------------------------------------------------------------
    def __str__(self):
        """
        Typecasting into a string for error output.
        """

        msg = "Function %s() has to be overridden in class '%s'."
        return msg % (self.function_name, self.class_name)

#==============================================================================
class PbIoTimeoutError(PbError, IOError):
    """
    Special error class indicating a timout error on a read/write operation
    """

    #--------------------------------------------------------------------------
    def __init__(self, strerror, timeout, filename = None):
        """
        Constructor.

        @param strerror: the error message about the operation
        @type strerror: str
        @param timeout: the timout in seconds leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        t_o = None
        try:
            t_o = float(timeout)
        except ValueError:
            pass
        self.timeout = t_o

        if t_o is not None:
            strerror += " (timeout after %0.1f secs)" % (t_o)

        if filename is None:
            super(PbIoTimeoutError, self).__init__(errno.ETIMEDOUT, strerror)
        else:
            super(PbIoTimeoutError, self).__init__(
                    errno.ETIMEDOUT, strerror, filename)

#==============================================================================
class PbReadTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on reading of a file.
    """

    #--------------------------------------------------------------------------
    def __init__(self, timeout, filename):
        """
        Constructor.

        @param timeout: the timout in second leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        strerror = "Timeout error on reading"
        super(PbReadTimeoutError, self).__init__(strerror, timeout, filename)

#==============================================================================
class PbWriteTimeoutError(PbIoTimeoutError):
    """
    Special error class indicating a timout error on a writing into a file.
    """

    #--------------------------------------------------------------------------
    def __init__(self, timeout, filename):
        """
        Constructor.

        @param timeout: the timout in second leading to the error
        @type timeout: float
        @param filename: the filename leading to the error
        @type filename: str

        """

        strerror = "Timeout error on writing"
        super(PbWriteTimeoutError, self).__init__(strerror, timeout, filename)

#==============================================================================

if __name__ == "__main__":
    pass

#==============================================================================

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nu
