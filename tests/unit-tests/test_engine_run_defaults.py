# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.opts import FetchdepEngineOptions
from tests import FetchdepTestCase
from tests import prepare_testenv
from tests import run_testenv
import os


class TestEngineRunDefaults(FetchdepTestCase):
    def test_engine_run_defaults_dirs(self):
        with prepare_testenv() as engine:
            # check if root directory is set
            work_dir = engine.opts.work_dir
            self.assertTrue(os.path.exists(work_dir))

    def test_engine_run_defaults_noconfig(self):
        rv = run_testenv()
        self.assertTrue(rv)

    def test_engine_run_defaults_options_parallel(self):
        with prepare_testenv() as engine:
            # default to only a single job at a time
            self.assertEqual(engine.opts.parallel, 1)

    def test_engine_run_defaults_options_logging(self):
        with prepare_testenv() as engine:
            # logging should be disabled by default
            self.assertFalse(engine.opts.debug)
            self.assertFalse(engine.opts.no_color_out)
            self.assertFalse(engine.opts.verbose)

    def test_engine_run_defaults_workdir(self):
        # veiry a work directory is set by default
        opts = FetchdepEngineOptions()
        self.assertIsNotNone(opts.work_dir)
        self.assertTrue(os.path.isdir(opts.work_dir))
