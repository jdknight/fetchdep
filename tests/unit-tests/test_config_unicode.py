# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from __future__ import unicode_literals
from fetchdep.config import Config
from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
import os


class TestConfigUnicode(FetchdepTestCase):
    def test_config_unicode(self):
        cfg_path = fetch_unittest_assets_dir('unicode', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertTrue(loaded)

        deps = cfg.extract()
        self.assertIsNotNone(deps)
        self.assertEqual(len(deps), 1)

        dependency = deps[0]
        self.assertEqual(dependency.name, '例')
