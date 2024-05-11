# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import prepare_testenv
from tests import prepare_workdir
import os


class TestEngineRunArgs(FetchdepTestCase):
    def test_engine_run_args_all_tags(self):
        config = {
            'all_tags': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.all_tags)

    def test_engine_run_args_assume_no(self):
        config = {
            'assume_no': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.assume_yes is not None)
            self.assertFalse(engine.opts.assume_yes)

    def test_engine_run_args_assume_yes(self):
        config = {
            'assume_yes': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.assume_yes)

    def test_engine_run_args_config_file(self):
        test_filename = 'test-config'

        # test full configuration path
        with prepare_workdir() as misc_dir:
            mock_config = os.path.join(misc_dir, test_filename)

            config = {
                'config': mock_config,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.conf_point, mock_config)

        # test relative to working directory path
        with prepare_workdir() as work_dir:
            config = {
                'config': test_filename,
                'work_dir': work_dir,
            }

            with prepare_testenv(config=config) as engine:
                mock_config = os.path.join(os.getcwd(), test_filename)
                self.assertEqual(engine.opts.conf_point, mock_config)

    def test_engine_run_args_debug(self):
        config = {
            'debug': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.debug)

    def test_engine_run_args_dryrun(self):
        config = {
            'dry_run': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.dry_run)

    def test_engine_run_args_nocolorout(self):
        config = {
            'nocolorout': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.no_color_out)

    def test_engine_run_args_parallel(self):
        config = {
            'parallel': 2,
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.parallel, 2)

        config = {
            'parallel': 0,
        }

        with prepare_testenv(config=config) as engine:
            self.assertGreater(engine.opts.parallel, 0)

    def test_engine_run_args_recursive(self):
        config = {
            'recursive': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.recursive)

    def test_engine_run_args_required(self):
        config = {
            'required': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.required)

    def test_engine_run_args_skip_missing(self):
        config = {
            'skip_missing': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.skip_missing)

    def test_engine_run_args_state(self):
        config = {
            'state': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.dump_state)

    def test_engine_run_args_verbose(self):
        config = {
            'verbose': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.verbose)

    def test_engine_run_args_work_dir(self):
        with prepare_workdir() as work_dir:
            config = {
                'work_dir': work_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.work_dir, work_dir)
