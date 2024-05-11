# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
from tests import prepare_testenv
import os


class TestEngineRunMissing(FetchdepTestCase):
    def test_engine_run_missing_allowed(self):
        cfg_path = fetch_unittest_assets_dir('missing', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'config': cfg_path,
            'skip_missing': True,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)

    def test_engine_run_missing_fail(self):
        cfg_path = fetch_unittest_assets_dir('missing', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'config': cfg_path,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertFalse(rv)
