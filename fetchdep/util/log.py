# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from __future__ import print_function
from __future__ import unicode_literals
from fetchdep.util.compat import make_unicode
import os
import sys


#: flag to track the enablement of debug messages
FETCHDEP_LOG_DEBUG_FLAG = False

#: flag to track the disablement of colorized messages
FETCHDEP_LOG_NOCOLOR_FLAG = False

#: flag to track the enablement of verbose messages
FETCHDEP_LOG_VERBOSE_FLAG = False


def log(msg, *args):
    """
    log a message

    Logs a (normal) message to standard out with a trailing new line.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '', msg, sys.stdout, *args)
    flush_stdout()


def debug(msg, *args):
    """
    log a debug message

    Logs a debug message to standard out with a trailing new line. By default,
    debug messages will not be output to standard out unless the instance is
    configured with debugging enabled.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if FETCHDEP_LOG_DEBUG_FLAG:
        __log('(debug) ', '\033[2m', msg, sys.stdout, *args)

def err(msg, *args):
    """
    log an error message

    Logs an error message to standard error with a trailing new line and (if
    enabled) a red colorization.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    flush_stdout()
    __log('(error) ', '\033[1;31m', msg, sys.stderr, *args)
    flush_stderr()


def flush_stderr():
    """
    force a flush of stderr

    Forces a flush of the stderr stream for both the application and operating
    systen.
    """
    sys.stderr.flush()
    try:
        os.fsync(sys.stderr.fileno())
    except (AttributeError, OSError):
        pass


def flush_stdout():
    """
    force a flush of stdout

    Forces a flush of the stdout stream for both the application and operating
    systen.
    """
    sys.stdout.flush()
    try:
        os.fsync(sys.stdout.fileno())
    except (AttributeError, OSError):
        pass


def hint(msg, *args):
    """
    log a hint message

    Logs a hint message to standard out with a trailing new line and (if
    enabled) a cyan colorization.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '\033[1;36m', msg, sys.stdout, *args)
    flush_stdout()


def is_debug():
    """
    report if the instance is configured with debug messaging

    Allows a caller to determine whether or not the instance is actively
    configured with debug messaging. This allow a caller to have the option to
    decide whether or not it needs to prepare a message for a ``debug`` call,
    if the message to be built may include a performance cost.

    Returns:
        whether the instance is configured with verbose messaging
    """
    return FETCHDEP_LOG_DEBUG_FLAG


def is_nocolor():
    """
    report if the instance is configured with nocolor messaging

    Allows a caller to determine whether or not the instance is actively
    configured with nocolor messaging.

    Returns:
        whether the instance is configured with nocolor messaging
    """
    return FETCHDEP_LOG_NOCOLOR_FLAG


def is_verbose():
    """
    report if the instance is configured with verbose messaging

    Allows a caller to determine whether or not the instance is actively
    configured with verbose messaging. This allow a caller to have the option to
    decide whether or not it needs to prepare a message for a ``verbose`` call,
    if the message to be built may include a performance cost.

    Returns:
        whether the instance is configured with verbose messaging
    """
    return FETCHDEP_LOG_VERBOSE_FLAG


def note(msg, *args):
    """
    log a notification message

    Logs a notification message to standard out with a trailing new line and (if
    enabled) an inverted colorization.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '\033[7m', msg, sys.stdout, *args)
    flush_stdout()


def success(msg, *args):
    """
    log a success message

    Logs a success message to standard error with a trailing new line and (if
    enabled) a green colorization.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('(success) ', '\033[1;32m', msg, sys.stdout, *args)
    flush_stdout()


def verbose(msg, *args):
    """
    log a verbose message

    Logs a verbose message to standard out with a trailing new line and (if
    enabled) an inverted colorization. By default, verbose messages will not be
    output to standard out unless the instance is configured with verbosity.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if FETCHDEP_LOG_VERBOSE_FLAG:
        __log('(verbose) ', '\033[2m', msg, sys.stdout, *args)


def warn(msg, *args):
    """
    log a warning message

    Logs a warning message to standard error with a trailing new line and (if
    enabled) a purple colorization.

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    flush_stdout()
    __log('(warn) ', '\033[1;35m', msg, sys.stderr, *args)
    flush_stderr()


def __log(prefix, color, msg, file, *args):
    """
    utility logging method

    A log method to help format a message based on provided prefix and color.

    Args:
        prefix: prefix to add to the message
        color: the color to apply to the message
        msg: the message
        file: the file to write to
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if FETCHDEP_LOG_NOCOLOR_FLAG:
        color = ''
        post = ''
    else:
        post = '\033[0m'

    msg = str(msg)
    msg = make_unicode(msg)
    if args:
        msg = msg.format(*args)
    print('{}{}{}{}'.format(color, prefix, msg, post), file=file)


def fetchdep_log_configuration(debug_, nocolor, verbose_):
    """
    configure the global logging state of the running instance

    Adjusts the running instance's active state for logging-related
    configuration values. This method is best invoked near the start of the
    process's life cycle to provide consistent logging output. This method does
    not required to be invoked to invoke provided logging methods.

    Args:
        debug_: toggle the enablement of debug messages
        nocolor: toggle the disablement of colorized messages
        verbose_: toggle the enablement of verbose messages
    """
    global FETCHDEP_LOG_DEBUG_FLAG
    global FETCHDEP_LOG_NOCOLOR_FLAG
    global FETCHDEP_LOG_VERBOSE_FLAG
    FETCHDEP_LOG_DEBUG_FLAG = debug_
    FETCHDEP_LOG_NOCOLOR_FLAG = nocolor
    FETCHDEP_LOG_VERBOSE_FLAG = verbose_
