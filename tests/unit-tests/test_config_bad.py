# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.config import Config
from fetchdep.exceptions import MissingNameConfigurationError
from fetchdep.exceptions import MissingSiteConfigurationError
from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
import os


class TestConfigBad(FetchdepTestCase):
    def test_config_bad_missing(self):
        cfg_path = fetch_unittest_assets_dir('does-not-exist', 'fetchdep.yml')
        self.assertFalse(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertFalse(loaded)

    def test_config_bad_no_name(self):
        cfg_path = fetch_unittest_assets_dir('badcfg-no-name', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertTrue(loaded)

        with self.assertRaises(MissingNameConfigurationError):
            cfg.extract()

    def test_config_bad_no_site(self):
        cfg_path = fetch_unittest_assets_dir('badcfg-no-site', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertTrue(loaded)

        with self.assertRaises(MissingSiteConfigurationError):
            cfg.extract()

    def test_config_bad_not_fetchdep(self):
        cfg_path = fetch_unittest_assets_dir(
            'badcfg-yaml-notfetchdep', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertFalse(loaded)

    def test_config_bad_yaml(self):
        cfg_path = fetch_unittest_assets_dir(
            'badcfg-yaml-syntax', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertFalse(loaded)
