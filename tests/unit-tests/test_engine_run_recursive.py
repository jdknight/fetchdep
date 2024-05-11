# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
from tests import prepare_testenv
import os


class TestEngineRunRecursive(FetchdepTestCase):
    def test_engine_run_recursive_disabled(self):
        expected = [
            'recursive',
        ]

        cfg_path = fetch_unittest_assets_dir('recursive', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'config': cfg_path,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)

            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), set(expected))

    def test_engine_run_recursive_enabled(self):
        expected = [
            'recursive',
            'fetchdep-a',
            'fetchdep-b',
            'fetchdep-c',
            'fetchdep-d',
            'fetchdep-e',
            'fetchdep-f',
            'fetchdep-g',
        ]

        cfg_path = fetch_unittest_assets_dir('recursive', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'config': cfg_path,
            'recursive': True,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)

            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), set(expected))
