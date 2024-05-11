# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from contextlib import contextmanager
from fetchdep.util.log import debug
from fetchdep.util.log import err
from fetchdep.util.log import is_verbose
from fetchdep.util.log import verbose
import errno
import os
import re
import subprocess
import sys
import unicodedata

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from shlex import quote
except ImportError:
    from pipes import quote

# invalid characters for a directory name
INVALID_DIRNAME_CHARS = r'["*/:\'<>\?\\|]'

# list of unsupported directory names
RESTRICTED_DIRNAMES = [
    '.',
    '..',
    'AUX',
    'COM1',
    'COM2',
    'COM3',
    'COM4',
    'COM5',
    'COM6',
    'COM7',
    'COM8',
    'COM9',
    'CON',
    'LPT1',
    'LPT2',
    'LPT3',
    'LPT4',
    'LPT5',
    'LPT6',
    'LPT7',
    'LPT8',
    'LPT9',
    'NUL',
    'PRN',
]


def execute(args, cwd=None, env=None, env_update=None, quiet=None,
        poll=False, capture=None):
    """
    execute the provided command/arguments

    Runs the command described by ``args`` until completion. A caller can adjust
    the working directory of the executed command by explicitly setting the
    directory in ``cwd``. The execution request will return the command's return
    code as well as any captured output.

    The environment variables used on execution can be manipulated in two ways.
    First, the environment can be explicitly controlled by applying a new
    environment content using the ``env`` dictionary. Key of the dictionary will
    be used as environment variable names, whereas the respective values will be
    the respective environment variable's value. If ``env`` is not provided, the
    existing environment of the executing context will be used. Second, a caller
    can instead update the existing environment by using the ``env_update``
    option. Like ``env``, the key-value pairs match to respective environment
    key-value pairs. The difference with this option is that the call will use
    the original environment values and update select values which match in the
    updated environment request. When ``env`` and ``env_update`` are both
    provided, ``env_update`` will be updated the options based off of ``env``
    instead of the original environment of the caller.

    In special cases, an executing process may not provide carriage returns/new
    lines to simple output processing. This can lead the output of a process to
    be undesirably buffered. To workaround this issue, the execution call can
    instead poll for output results by using the ``poll`` option with a value
    of ``True``. By default, polling is disabled with a value of ``False``.

    A caller may wish to capture the provided output from a process for
    examination. If a list is provided in the call argument ``capture``, the
    list will be populated with the output provided from an invoked process.

    Args:
        args: the list of arguments to execute
        cwd (optional): working directory to use
        env (optional): environment variables to use for the process
        env_update (optional): environment variables to append for the process
        quiet (optional): whether or not to suppress output (defaults to
            ``False``)
        poll (optional): force polling stdin/stdout for output data (defaults to
            ``False``)
        capture (optional): list to capture output into

    Returns:
        the return code of the execution request
    """

    # append provided environment updates (if any) to the provided or existing
    # environment dictionary
    final_env = None
    if env:
        final_env = dict(env)
    if env_update:
        if not final_env:
            final_env = os.environ.copy()
        final_env.update(env_update)

    # if quiet is undefined, default its state based on whether or not the
    # caller wishes to capture output to a list
    if quiet is None:
        quiet = capture is not None

    cmd_str = None
    rv = 1
    if args:
        # force any `None` arguments to empty strings, as a subprocess request
        # will not accept it; ideally, a call should not be passing a `None`
        # entry, but providing flexibility when it has been done
        args = [arg if arg is not None else '' for arg in args]

        # attempt to always invoke using a script's interpreter (if any) to
        # help deal with long-path calls
        if sys.platform != 'win32':
            args = prepend_shebang_interpreter(args)

        # python 2.7 can have trouble with unicode environment variables;
        # forcing all values to an ascii type
        if final_env and sys.version_info[0] < 3:  # noqa: PLR2004
            debug('detected python 2.7; sanity checking environment variables')
            for k, v in final_env.items():
                if isinstance(v, unicode):  # pylint: disable=E0602 # noqa: F821
                    final_env[k] = v.encode('ascii', 'replace')

        if is_verbose():
            debug('(wd) {}', cwd if cwd else os.getcwd())
            cmd_str = _cmd_args_to_str(args)
            verbose('invoking: ' + cmd_str)
            sys.stdout.flush()

        try:
            # check if this execution should poll (for carriage returns and new
            # lines); note if quiet mode is enabled, do not attempt to poll
            # since none of the output will be printed anyways.
            if poll and not quiet:
                debug('will poll process for output')
                bufsize = 0
                universal_newlines = False
            else:
                bufsize = 1
                universal_newlines = True

            proc = subprocess.Popen(
                args,
                bufsize=bufsize,
                cwd=cwd,
                env=final_env,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                universal_newlines=universal_newlines,
            )

            if bufsize == 0:
                line = bytearray()
                while True:
                    c = proc.stdout.read(1)
                    if not c and proc.poll() is not None:
                        break
                    line += c
                    if c in (b'\r', b'\n'):
                        decoded_line = line.decode('utf_8')
                        if c == b'\n' and capture is not None:
                            capture.append(decoded_line)
                        if not quiet:
                            sys.stdout.write(decoded_line)
                            sys.stdout.flush()
                        del line[:]
            else:
                for line in iter(proc.stdout.readline, ''):
                    if capture is not None or not quiet:
                        line = line.rstrip()
                        if capture is not None:
                            capture.append(line)
                        if not quiet:
                            print(line)
                            sys.stdout.flush()
            proc.communicate()

            rv = proc.returncode
        except OSError as e:
            if not quiet:
                if not cmd_str:
                    cmd_str = _cmd_args_to_str(args)

                err('unable to execute command: {}\n'
                    '    {}', cmd_str, e)

    if rv != 0:
        if args:
            debug('failed to issue last command')
        else:
            debug('failed to issue an empty command')

    return rv


def makedirs(dir_, quiet=False):
    """
    ensure the provided directory exists

    Attempts to create the provided directory. If the directory already exists,
    this method has no effect. If the directory does not exist and could not be
    created, this method will return ``False``. Also, if an error has been
    detected, an error message will be output to standard error (unless
    ``quiet`` is set to ``True``).

    Args:
        dir_: the directory
        quiet (optional): whether or not to suppress output (defaults to
            ``False``)

    Returns:
        ``True`` if the directory exists; ``False`` if the directory could not
        be created
    """
    try:
        os.makedirs(dir_)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(dir_):
            if not quiet:
                err('unable to create directory: {}\n'
                    '    {}', dir_, e)
            return False
    return True


def prepend_shebang_interpreter(args):
    """
    prepend interpreter program (if any) to argument list

    When invoking an executable defines an interpreter beyond system limits,
    the system may be unable to handle the request. Instead of relying on the
    system to extract the interpreter directive from a script, extract the value
    and prepend the program (and possibly argument) to the returned argument
    list. In the event that no interpreter directive exists (or is unsupported),
    this method will return the same ``args`` value.

    Args:
        args: the argument list

    Returns:
        the final argument list
    """
    try:
        with open(args[0], 'rb') as f:
            if f.read(1) == b'#' and f.read(1) == b'!':
                MAXINTERP = 2048
                interp = f.readline(MAXINTERP + 1).rstrip()
                if len(interp) > MAXINTERP:
                    return args
                interp_args = interp.split(None, 1)[:2]
                return interp_args + [arg.encode() for arg in args]
    except (IOError, UnicodeError):
        pass
    return args


@contextmanager
def redirect_output(new_target=None):
    """
    temporarily redirect stderr and stdout to another instance

    This call will temporarily redirect stderr and stdout to the provided
    instance until the end of the context, where the previous targets will be
    restored.

    Args:
        new_target (optional): the instance to map stderr/stdout to
    """

    if not new_target:
        new_target = StringIO()

    original_stderr = sys.stderr
    original_stdout = sys.stdout
    try:
        sys.stderr = new_target
        sys.stdout = new_target
        yield new_target
    finally:
        sys.stderr = original_stderr
        sys.stdout = original_stdout


def resolve_dirname(dirname):
    """
    resolve a directory name

    Accepts a provided directory name and validates that the provided name
    is valid to be used in a file system. This ensures each character used is
    usable for a file path or the final directory does not use a
    system-reserved name. The directory name is normalize and stripped.

    Args:
        dirname: the directory name to check/normalize/cleanup

    Returns:
        the resolved directory name

    Raises:
        ValueError: when an invalid name is provided
    """

    if not dirname:
        msg = 'empty name'
        raise ValueError(msg)

    # stop if using an unsupported character
    #if any(INVALID_DIRNAME_CHARS in c for c in dirname):
    if re.search(INVALID_DIRNAME_CHARS, dirname):
        msg = 'invalid characters in name'
        raise ValueError(msg)

    # normalize a unicode name
    final_dirname = unicodedata.normalize('NFKC', dirname)

    # remove any leading/trailing whitespaces
    final_dirname = final_dirname.strip()

    if not final_dirname:
        msg = 'empty name after normalize/strip'
        raise ValueError(msg)

    if final_dirname in RESTRICTED_DIRNAMES:
        msg = 'restricted name'
        raise ValueError(msg)

    return final_dirname


def _cmd_args_to_str(args):
    """
    convert an argument list to a platform escaped string

    This call attempts to convert a list of arguments (to be passed into a
    `subprocess.Popen` request) into a string value. This is primarily to help
    support logging commands for a user in error/verbose scenarios to minimize
    the effort needed to manually re-invoke a command in a shell.

    Args:
        args: the argument list

    Returns:
        the argument(s) represented as a single string
    """
    if sys.platform == 'win32':
        cmd_str = subprocess.list2cmdline(args)
    else:
        cmd_str = ''
        for arg in args:
            if isinstance(arg, bytes):
                arg = arg.decode('utf_8')
            cmd_str += ' ' + quote(arg)
        cmd_str = cmd_str.strip()

    return cmd_str
