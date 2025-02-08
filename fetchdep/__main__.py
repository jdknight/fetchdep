#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep import __version__ as fetchdep_version
from fetchdep.engine import FetchdepEngine
from fetchdep.exceptions import FetchdepError
from fetchdep.opts import FetchdepEngineOptions
from fetchdep.util.log import debug
from fetchdep.util.log import err
from fetchdep.util.log import fetchdep_log_configuration
from fetchdep.util.log import log
from fetchdep.util.log import warn
from fetchdep.util.win32 import enable_ansi as enable_ansi_win32
import argparse
import os
import sys


def main():
    """
    mainline

    The mainline for fetchdep.

    Returns:
        the exit code
    """
    retval = 1

    try:
        parser = argparse.ArgumentParser(
            prog='fetchdep', add_help=False, usage=usage())

        parser.add_argument('target', nargs='?')
        parser.add_argument('--all-tags', action='store_true')
        parser.add_argument('--assume-no', action='store_true')
        parser.add_argument('--assume-yes', '-y', action='store_true')
        parser.add_argument('--config', '-C')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--parallel', '-p', '--jobs', '-j',
            const=0, nargs='?', type=type_nonnegativeint)
        parser.add_argument('--recursive', '-R', action='store_true')
        parser.add_argument('--required', action='store_true')
        parser.add_argument('--skip-missing', '-s', action='store_true')
        parser.add_argument('--state', action='store_true')
        parser.add_argument('--tag', action='append')
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', '-v', action='version',
            version='%(prog)s ' + fetchdep_version)
        parser.add_argument('--work-dir')

        args = parser.parse_args()
        if args.help:
            print(usage())
            sys.exit(0)

        # force verbose messages if debugging is enabled
        if args.debug:
            args.verbose = True

        # force color off if `NO_COLOR` is configured
        if os.getenv('NO_COLOR'):
            args.nocolorout = True

        # prepare logging
        fetchdep_log_configuration(args.debug, args.nocolorout, args.verbose)

        # toggle on ansi colors by default for commands
        if not args.nocolorout:
            os.environ['CLICOLOR_FORCE'] = '1'

            # support character sequences (for color output on win32 cmd)
            if sys.platform == 'win32':
                enable_ansi_win32()

        # banner
        log('fetchdep {}', fetchdep_version)
        debug('({})', __file__)

        if args.dry_run:
            warn('[dry-run] performing a dry-run')

        # prepare engine options
        opts = FetchdepEngineOptions(args=args)

        # create and start the engine
        engine = FetchdepEngine(opts)
        try:
            if engine.run():
                retval = 0
        except FetchdepError as e:
            err(e)
    except KeyboardInterrupt:
        print()

    return retval


def type_nonnegativeint(value):
    """
    argparse type check for a non-negative integer

    Provides a type check for an argparse-provided argument value to ensure the
    value is a non-negative integer value.

    Args:
        value: the value to check

    Returns:
        the non-negative integer value

    Raises:
        argparse.ArgumentTypeError: detected an invalid non-negative value
    """
    val = int(value)
    if val < 0:
        msg = 'invalid non-negative value'
        raise argparse.ArgumentTypeError(msg)
    return val


def usage():
    """
    display the usage for this tool

    Returns a command line usage string for all options available by fetchdep.

    Returns:
        the usage string
    """
    return """fetchdep <options> [target]

 --all-tags                Include all dependencies that have a tag
 --assume-no               Automatically answer no for any question
 --assume-yes, -y          Automatically answer yes for any question
 --config <file>, -C       Configuration file to load
 --debug                   Show debug-related messages
 --dry-run                 Perform a dry-run of what will be fetched
 --help, -h                Show this help
 --nocolorout              Explicitly disable colorized output
 --parallel [<count>], -p  Enable parallel fetching
 --recursive, -R           Allow fetching dependency's dependencies
 --required                Require a configuration to exist
 --skip-missing, -s        Continue even if a dependency cannot be fetched
 --state                   Dump the state of this tool
 --tag <value>             Tags to use
 --verbose, -V             Show additional messages
 --version, -v             Show the version
 --work-dir <dir>          Directory to fetch content
"""


if __name__ == '__main__':
    sys.exit(main())
