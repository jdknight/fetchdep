# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
from tests import prepare_testenv
import os


class TestEngineRunLarge(FetchdepTestCase):
    def test_engine_run_large_deny(self):
        cfg_path = fetch_unittest_assets_dir('large-set', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'assume_no': True,
            'config': cfg_path,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertFalse(rv)

    def test_engine_run_large_permit(self):
        cfg_path = fetch_unittest_assets_dir('large-set', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'assume_yes': True,
            'config': cfg_path,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)
