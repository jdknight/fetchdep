# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from contextlib import contextmanager
from fetchdep.engine import FetchdepEngine
from fetchdep.opts import FetchdepEngineOptions
from fetchdep.util.log import err
from fetchdep.util.log import warn
import errno
import os
import stat
import sys
import tempfile
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def ensure_dir_exists(dir_):
    """
    ensure the provided directory exists

    Attempts to create the provided directory. If the directory already exists,
    this method has no effect. If the directory does not exist and could not be
    created, this method will return ``False``. Also, if an error has been
    detected, an error message will be output to standard error.

    Args:
        dir_: the directory

    Returns:
        ``True`` if the directory exists; ``False`` if the directory could not
        be created
    """
    try:
        os.makedirs(dir_)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(dir_):
            err('unable to create directory: {}\n'
                '    {}', dir_, e)
            return False
    return True


@contextmanager
def generate_temp_dir(dir_=None):
    """
    generate a context-supported temporary directory

    Creates a temporary directory in the provided directory ``dir_`` (or system
    default, is not provided). This is a context-supported call and will
    automatically remove the directory when completed. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareBaseDirectoryError`` exception will be thrown.

    Args:
        dir_ (optional): the directory to create the temporary directory in

    Raises:
        FailedToPrepareBaseDirectoryError: the base directory does not exist and
            could not be created
    """
    if dir_ and not ensure_dir_exists(dir_):
        raise FailedToPrepareBaseDirectoryError(dir_)

    dir_ = tempfile.mkdtemp(prefix='.fetchdep-tmp-', dir=dir_)
    try:
        yield dir_
    finally:
        try:
            path_remove(dir_)
        except OSError as e:
            if e.errno != errno.ENOENT:
                warn('unable to cleanup temporary directory: {}\n'
                     '    {}', dir_, e)


@contextmanager
def interim_working_dir(dir_):
    """
    move into a context-supported working directory

    Moves the current context into the provided working directory ``dir``. When
    returned, the original working directory will be restored. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareWorkingDirectoryError`` exception will be
    thrown.

    Args:
        dir_: the target working directory

    Raises:
        FailedToPrepareWorkingDirectoryError: the working directory does not
            exist and could not be created
    """
    owd = os.getcwd()

    if not ensure_dir_exists(dir_):
        raise FailedToPrepareWorkingDirectoryError(dir_)

    os.chdir(dir_)
    try:
        yield dir_
    finally:
        try:
            os.chdir(owd)
        except IOError:
            warn('unable to restore original working directory: ' + owd)


def path_remove(path):
    """
    remove the provided path

    Attempts to remove the provided path if it exists. The path value can either
    be a directory or a specific file. If the provided path does not exist, this
    method has no effect. In the event that a file or directory could not be
    removed due to an error other than unable to be found, an error message will
    be output to standard error.

    Args:
        path: the path to remove

    Returns:
        ``True`` if the path was removed or does not exist; ``False`` if the
        path could not be removed from the system
    """

    if not os.path.exists(path):
        return True

    try:
        if os.path.isdir(path) and not os.path.islink(path):
            _path_remove_dir(path)
        else:
            _path_remove_file(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            err('unable to remove path: {}\n'
                '    {}', path, e)
            return False

    return True


def _path_remove_dir(dir_):
    """
    remove the provided directory (recursive)

    Attempts to remove the provided directory. In the event that a file or
    directory could not be removed due to an error, this function will typically
    raise an OSError exception.

    In the chance that a file cannot be removed due to permission issues, this
    function can attempt to adjust permissions to specific paths to help in the
    removal processes (e.g. dealing with read-only files or other strict
    permissions setup during a build process).

    Args:
        dir_: the directory to remove

    Raises:
        OSError: if a path could not be removed
    """

    # ensure a caller has read/write access before hand to prepare for removal
    # (e.g. if marked as read-only) and ensure contents can be fetched as well
    try:
        st = os.stat(dir_)
        if not (st.st_mode & stat.S_IRUSR) or not (st.st_mode & stat.S_IWUSR):
            os.chmod(dir_, st.st_mode | stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    # remove directory contents (if any)
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.isdir(path) and not os.path.islink(path):
            _path_remove_dir(path)
        else:
            _path_remove_file(path)

    # remove directory
    os.rmdir(dir_)


def _path_remove_file(path):
    """
    remove the provided file

    Attempts to remove the provided file. In the event that the file could not
    be removed due to an error, this function will typically raise an OSError
    exception.

    In the chance that a file cannot be removed due to permission issues, this
    function can attempt to adjust permissions to specific paths to help in the
    removal processes (e.g. dealing with read-only files or other strict
    permissions setup during a build process).

    Args:
        path: the file to remove

    Raises:
        OSError: if the file could not be removed
    """

    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.EACCES:
            raise

        # if a file could not be removed, try adding write permissions
        # and retry removal
        try:
            st = os.stat(path)
            if (st.st_mode & stat.S_IWUSR):
                raise

            os.chmod(path, st.st_mode | stat.S_IWUSR)
            os.remove(path)
        except OSError:
            raise e


@contextmanager
def prepare_testenv(config=None):
    """
    prepare an engine-ready environment for a test

    This utility method is used to provide an `FetchdepEngine` instance ready
    for execution on an interim working directory.

    Args:
        config (optional): dictionary of options to mock for arguments

    Yields:
        the engine
    """

    class MockArgs(object):
        def __getattr__(self, name):
            return self.name if name in self.__dict__ else None

    config = {} if config is None else dict(config)

    with generate_temp_dir() as work_dir, interim_working_dir(work_dir):
        if 'work_dir' not in config:
            config['work_dir'] = work_dir

        # build arguments instance
        test_args = MockArgs()
        for k, v in config.items():
            setattr(test_args, k, v)

        # prepare engine options and build an engine instance
        opts = FetchdepEngineOptions(args=test_args)
        engine = FetchdepEngine(opts)

        yield engine


@contextmanager
def prepare_workdir():
    """
    prepare a working directory for a test

    This utility method is used to provide a test a directory to store
    output files. This method will ensure the container directory is emptied
    before returning.

    Returns:
        the container directory
    """

    with generate_temp_dir() as work_dir:
        yield work_dir


@contextmanager
def redirect_stderr(new_target=None):
    """
    temporarily redirect stderr to another instance

    This call will temporarily redirect stderr to the provided instance
    until the end of the context, where the previous `stderr` target will be
    restored.

    Args:
        new_target (optional): the instance to map stderr to
    """

    if not new_target:
        new_target = StringIO()

    _ = sys.stderr
    try:
        sys.stderr = new_target
        yield new_target
    finally:
        sys.stderr = _


@contextmanager
def redirect_stdout(new_target=None):
    """
    temporarily redirect stdout to another instance

    This call will temporarily redirect stdout to the provided instance
    until the end of the context, where the previous `stdout` target will be
    restored.

    Args:
        new_target (optional): the instance to map stdout to
    """

    print(type(sys.stderr))
    if not new_target:
        new_target = StringIO()

    _ = sys.stdout
    try:
        sys.stdout = new_target
        yield new_target
    finally:
        sys.stdout = _


def run_testenv(config=None):
    """
    execute an engine instance with provide environment options for a test

    This utility method is used to invoke an `FetchdepEngine` instance which is
    prepared based off the provided configuration options .

    Args:
        config (optional): dictionary of options to mock for arguments

    Returns:
        the engine's return code
    """

    with prepare_testenv(config=config) as engine:
        return engine.run()


def find_test_base():
    """
    return the absolute path of the test base directory

    A utility call to return the absolute path of the "tests" directory for this
    implementation. This is to support interpreters (i.e. Python 2.7) which do
    not provide an absolute path via the `__file__` variable.

    Returns:
        the path
    """

    test_base = os.path.dirname(os.path.realpath(__file__))

    def unit_tests_exist(test_base):
        return os.path.exists(os.path.join(test_base, 'unit-tests'))

    if not unit_tests_exist(test_base):
        test_base = os.path.dirname(os.path.abspath(sys.argv[0]))
        if not unit_tests_exist(test_base):
            # python 2.7 may not always be able to find the test directory at
            # all stages of test; try to rely on a provided tox ini directory if
            # running in a tox environment
            if sys.version_info < (3, 0) and 'TOX_INI_DIR' in os.environ:
                root_dir = os.environ['TOX_INI_DIR']
                test_base = os.path.join(root_dir, 'tests')

            if not unit_tests_exist(test_base):
                msg = 'unable to find test base directory'
                raise RuntimeError(msg)

    return test_base


def fetch_unittest_assets_dir(*args):
    """
    fetch the unit tests assets directory

    Will return the full path for the unit testing's asset directory.

    Args:
        *args (optional): path entries to append to the asset directory

    Returns:
        the directory
    """
    base_dir = find_test_base()
    return os.path.join(base_dir, 'unit-tests', 'assets', *args)


class FetchdepTestSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        """
        a fetchdep helper test suite

        Provides a `unittest.TestSuite` which will ensure stdout is flushed
        after the execution of tests. This is to help ensure all stdout content
        from the test is output to the stream before the unittest framework
        outputs a test result summary which may be output to stderr.

        See `unittest.TestSuite.run()` for more details.

        Args:
            result: the test result object to populate
            debug (optional): debug flag to ignore error collection

        Returns:
            the test result object
        """
        rv = unittest.TestSuite.run(self, result, debug)
        sys.stdout.flush()
        return rv


class FetchdepTestCase(unittest.TestCase):
    """
    a fetchdep unit test case

    Provides a `unittest.TestCase` implementation that fetchdep unit
    tests should inherit from. This test class provides the following
    capabilities:

    - Clears the running environment back to its original state after
       each test run. fetchdep events will populate the running environment
       for project scripts to use. Ensuring the environment is clean after
       each run prevents tests to conflicting with each other's state.
    """

    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed
        as result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with self.env_wrap():
            super(FetchdepTestCase, self).run(result)

    @contextmanager
    def env_wrap(self):
        """
        wrap the context's environment

        This context method provides a way restrict environment changes to the
        context.
        """

        old_env = dict(os.environ)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_env)


class FetchdepExtractTestCase(FetchdepTestCase):
    """
    a fetchdep unit test case

    Provides a `unittest.TestCase` implementation that fetchdep unit
    tests should inherit from. This test class provides the following
    capabilities:

    - Clears the running environment back to its original state after
       each test run. fetchdep events will populate the running environment
       for project scripts to use. Ensuring the environment is clean after
       each run prevents tests to conflicting with each other's state.
    """

    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed
        as result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with generate_temp_dir() as repo_dir, interim_working_dir(repo_dir):
            self.repo_dir = repo_dir
            super(FetchdepExtractTestCase, self).run(result)


class FailedToPrepareBaseDirectoryError(Exception):
    """
    raised when a base directory could not be prepared
    """


class FailedToPrepareWorkingDirectoryError(Exception):
    """
    raised when a working directory could not be prepared
    """
