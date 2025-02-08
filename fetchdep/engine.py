# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.config import Config
from fetchdep.config import find_configuration
from fetchdep.database import ConfigDatabase
from fetchdep.defs import MAX_REQUEST_BEFORE_CONFIRM
from fetchdep.exceptions import FetchdepMissingConfigurationError
from fetchdep.fetch import prepare_fetch_request
from fetchdep.processor import ProcessState
from fetchdep.processor import process
from fetchdep.processor import process_initialization
from fetchdep.util.compat import compat_input
from fetchdep.util.log import debug
from fetchdep.util.log import err
from fetchdep.util.log import is_debug
from fetchdep.util.log import is_nocolor
from fetchdep.util.log import is_verbose
from fetchdep.util.log import log
from fetchdep.util.log import success
from fetchdep.util.log import verbose
from fetchdep.util.log import warn
from yaml import __version__ as yaml_version
import multiprocessing
import os
import sys

if sys.version_info < (3, 0):
    import imp


class FetchdepEngine:
    def __init__(self, opts):
        """
        fetchdep's engine

        The "engine" performs the main fetchdep actions.

        Args:
            opts: options used to configure the engine

        Attributes:
            cfgdb: configuration database
            opts: options used to configure the engine
        """
        self.cfgdb = ConfigDatabase()
        self.opts = opts

        # find implementation location (mainly for debugging)
        if sys.version_info < (3, 0) and not os.path.isabs(__file__):
            _, self._base_dir, _ = imp.find_module(  # pylint: disable=E0606
                'fetchdep')
        else:
            engine_dir = os.path.dirname(__file__)
            self._base_dir = os.path.dirname(engine_dir)

    def run(self):
        """
        run the engine

        Starts the fetchdep process of parsing dependencies from a
        configuration and cloning their content.

        Returns:
            ``True`` if the engine has completed without error; ``False`` if an
            issue has occurred when interpreting or running the user's
            configuration/package definitions
        """

        opts = self.opts

        # verify the configuration exists before processing
        verbose('detecting configuration...')
        conf_point = opts.conf_point
        if conf_point and not os.path.exists(conf_point):
            raise FetchdepMissingConfigurationError(conf_point)

        # if no configuration is provided, attempt to load a default one from
        # the target directory; if none is found, stop successfully
        if not conf_point:
            conf_point = find_configuration(opts.target_dir)

            if not conf_point:
                if opts.required:
                    err('no configuration')
                    return False

                log('no configuration')
                return True

        # first pass configuration processing
        if not self._process_configuration(conf_point):
            return False

        # if a user only wants an initial state information, dump and stop
        if opts.dump_state:
            self._dump_state()
            return True

        # compile a list of dependencies that look to be missing
        missing_deps = []
        for dep in self.cfgdb.db.values():
            target_dir = os.path.join(opts.work_dir, dep.name)
            if not os.path.exists(target_dir):
                missing_deps.append(dep)

        unknown_tags = set(self.opts.tags) - self.cfgdb.tags
        if unknown_tags:
            warn('unknown tags: {}', ', '.join(sorted(unknown_tags)))

        if not missing_deps:
            success('no missing dependencies')
            return True

        debug('prepare worker pool state')
        process_state = ProcessState()

        # relay logging configuration state to other processes
        process_state.log_debug = is_debug()
        process_state.log_nocolor = is_nocolor()
        process_state.log_verbose = is_verbose()

        debug('starting worker pool ({})', opts.parallel)
        worker_pool = multiprocessing.Pool(processes=opts.parallel,
            initializer=process_initialization,
            initargs=(process_state,))

        trouble = False
        partial = False
        try:
            total_requests = 0
            while missing_deps:
                # if we are processing too many requests, ask the user if they
                # are sure they want to continue
                total_requests += len(missing_deps)
                if total_requests > MAX_REQUEST_BEFORE_CONFIRM:
                    if opts.assume_yes is None:
                        log('Reached a total of {} requests.', total_requests)
                        try:
                            while True:
                                rsp = compat_input('Continue requests? [y/N] ')
                                rsp = rsp.lower()
                                if rsp == 'y':
                                    opts.assume_yes = True
                                    break

                                if rsp in ('', 'n'):
                                    opts.assume_yes = False
                                    break

                                warn('Invalid response.')
                        except EOFError:
                            opts.assume_yes = False

                    if opts.assume_yes is False:
                        err('Stopping due to request limit.')
                        trouble = True
                        break

                # queue up a fetch request for each missing dependency and
                # pass the job into the work pool
                for dep in missing_deps:
                    req = prepare_fetch_request(dep, opts)

                    debug('queuing dependency: {}', dep.name)
                    process_state.queued()
                    req = worker_pool.apply_async(process, args=(req, opts))
                    debug('dependency has been queued: {}', dep.name)

                    # we primarily only perform a get here to help check for
                    # any immediate failures when invoking the async fetch
                    # request; as the get will fail and print any exception
                    # resulting from the multiprocessing event
                    try:
                        req.get(1)
                    except multiprocessing.TimeoutError:
                        pass

                # all missing dependencies have been queued; clear
                missing_deps = []

                debug('waiting for dependencies to be fetched')
                new_cfg = process_state.wait()

                if process_state.failure.value:
                    partial = True

                    if not opts.skip_missing:
                        trouble = True
                        debug('stop processing due to detected failure')
                        break

                # if we have a new configuration and recursive mode is enabled,
                # try to parse the configuration and add new dependencies to
                # the database to be processed
                if new_cfg and self.opts.recursive:
                    def hne(name):
                        # detected a new dependency; add it to the missing
                        # list so that it can be fetched next pass
                        new_dep = self.cfgdb.get(name)
                        missing_deps.append(new_dep)  # noqa: B023

                    debug('checking for new dependencies in: {}', new_cfg)
                    if not self._process_configuration(new_cfg, new_hook=hne):
                        trouble = True

                        if not opts.skip_missing:
                            debug('stop processing due to failed cfg-parse')
                            break

            debug('dependency processing has completed')
            worker_pool.close()
        except BaseException:
            trouble = True
            debug('signalling worker pool to stop')
            worker_pool.terminate()

            raise
        finally:
            debug('waiting for worker pool to complete')
            worker_pool.join()

        if trouble:
            return False

        if partial:
            warn('not all dependencies prepared')
        else:
            success('all dependencies prepared')

        return True

    def _process_configuration(self, conf_point, new_hook=None):
        cfg = Config()
        if not cfg.load(conf_point):
            return False

        additional_cfgs = []

        deps = cfg.extract()
        for dep in deps:
            # keep track of all known tags
            self.cfgdb.track_tags(dep.tags)

            # ignore already processed entries
            if self.cfgdb.exists(dep.name):
                debug('ignoring already registered dependency: {}', dep.name)
                continue

            # exclude dependencies that do not match tag configuration
            if not self.opts.all_tags and dep.tags:
                if not any(tag in dep.tags for tag in self.opts.tags):
                    continue

            self.cfgdb.store(dep.name, dep)
            if new_hook:
                new_hook(dep.name)

            # if recursive is enabled, check if this new dependency has any
            # fetchdep configuration to add even more dependencies
            if self.opts.recursive and dep.recursive:
                debug('check if package has a fetchdep config: {}', dep.name)
                expected_dir = os.path.join(self.opts.work_dir, dep.name)
                if os.path.exists(expected_dir):
                    new_conf = find_configuration(expected_dir)
                    if new_conf:
                        verbose('new dependency configuration: {}', new_conf)
                        additional_cfgs.append(new_conf)

        for additional_cfg in additional_cfgs:
            if not self._process_configuration(additional_cfg):
                return False

        return True

    def _dump_state(self):
        log('Python {}', sys.version)
        log('YAML {}', yaml_version)
        log('Tool: {}', self._base_dir)
        log('Target container: {}', self.opts.work_dir)

        # report any unused tags
        if not self.opts.all_tags:
            unused_tags = self.cfgdb.tags - set(self.opts.tags)
            if unused_tags:
                log('Unused tags: {}', ', '.join(sorted(unused_tags)))

        if self.cfgdb.db:
            log('Detected dependencies:')
            for name, val in self.cfgdb.db.items():
                expected_dir = os.path.join(self.opts.work_dir, name)

                state = ''
                if not os.path.exists(expected_dir):
                    state = ' (pending)'

                log('  {}{}', name, state)
                log('    Site: {}', val.site)
                log('    Type: {}', val.vcs)
                log('    Tags: {}', ','.join(val.tags) or '(none)')
        else:
            log('No detected dependencies.')
