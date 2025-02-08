# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

import multiprocessing
import os


class FetchdepEngineOptions:
    """
    engine options

    Configuration options to be passed into an engine instance.

    Args:
        args (optional): handle user-provided configuration options (argparse)
            and apply them to respective attributes

    Attributes:
        all_tags: include all dependencies that have tags
        assume_yes: automatically answer yes for any question
        conf_point: fetchdep configuration
        debug: whether debug messages are shown
        dry_run: perform a dry-run of what will be fetched
        dump_state: whether to only dump the running state
        no_color_out: whether colored messages are shown
        parallel: number of calculated jobs to allow at a given time
        recursive: allow fetching dependency's dependencies
        required: require that the default configuration exists
        skip_missing: continue even if a dependency cannot be fetched
        tags: desired tags to include
        target_dir: the context directory for a run
        verbose: whether verbose messages are shown
        work_dir: directory container to clone sources
    """
    def __init__(self, args=None):
        self.all_tags = False
        self.assume_yes = None
        self.conf_point = None
        self.debug = False
        self.dry_run = False
        self.dump_state = False
        self.no_color_out = False
        self.parallel = 1
        self.recursive = False
        self.required = False
        self.skip_missing = False
        self.tags = []
        self.target_dir = None
        self.verbose = False
        self.work_dir = None

        if args:
            self._handle_arguments(args)
        self._handle_environment_opts()
        self._finalize_options()

    def _handle_arguments(self, args):
        """
        handle argparse-processed arguments to populate engine options

        Accepts the result of an argparse's parsed arguments and updates
        engine options with respective argument options.

        Args:
            args: the arguments
        """

        if args.target:
            self.target_dir = os.path.abspath(args.target)

        if args.work_dir:
            self.work_dir = os.path.abspath(args.work_dir)

        self.all_tags = args.all_tags
        self.conf_point = args.config
        self.debug = args.debug
        self.dry_run = args.dry_run
        self.dump_state = args.state
        self.no_color_out = args.nocolorout
        self.recursive = args.recursive
        self.required = args.required
        self.skip_missing = args.skip_missing
        self.verbose = args.verbose

        if args.tag:
            self.tags.extend(args.tag)

        # if parallel is set to >1, use it; if not, a zero value is either
        # an indication that a user provided zero or no option was set, which
        # we want to clear to ensure an automatic count is performed
        if args.parallel is not None and args.parallel > 1:
            self.parallel = args.parallel
        elif args.parallel == 0:
            self.parallel = None

        if args.assume_no:
            self.assume_yes = False
        elif args.assume_yes:
            self.assume_yes = True

    def _handle_environment_opts(self):
        """
        handle environment variables to populate engine options

        Configure various options which support assignment from an
        environment variable.
        """

        if os.getenv('FETCHDEP_DEBUG'):
            self.debug = True
            self.verbose = True
        if os.getenv('FETCHDEP_VERBOSE'):
            self.verbose = True

    def _finalize_options(self):
        """
        finalize all engine options for use

        Ensures all options are properly configured to expected values to ensure
        default values are set which may depend on other currently provided
        options.
        """

        if not self.target_dir:
            self.target_dir = os.getcwd()

        if not self.work_dir:
            container_dir = os.path.join(self.target_dir, os.pardir)
            self.work_dir = os.path.abspath(container_dir)

        if self.conf_point and not os.path.isabs(self.conf_point):
            self.conf_point = os.path.join(self.target_dir, self.conf_point)
            self.conf_point = os.path.abspath(self.conf_point)

        if not self.parallel:
            try:
                # if `sched_getaffinity` is available, use the call the acquire
                # the number of physical cores on the system
                self.parallel = len(os.sched_getaffinity(0))
            except AttributeError:
                # if we cannot guarantee the number of physical cores, make an
                # assumption that the physical core count is half of the
                # (possible logical) core count provided by `cpu_count`
                cpu_count = multiprocessing.cpu_count()
                fuzzy_phy_cores = max(int(cpu_count / 2), 1)
                self.parallel = fuzzy_phy_cores
