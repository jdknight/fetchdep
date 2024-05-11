# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.config import find_configuration
from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
import os


class TestConfigFind(FetchdepTestCase):
    def test_config_find_missing(self):
        no_cfg_dir = fetch_unittest_assets_dir('no-config')
        self.assertTrue(os.path.isdir(no_cfg_dir))

        cfg = find_configuration(no_cfg_dir)
        self.assertIsNone(cfg)

    def test_config_find_type01(self):
        prj_dir = fetch_unittest_assets_dir('cfgname-type01')
        self.assertTrue(os.path.isdir(prj_dir))

        cfg = find_configuration(prj_dir)
        self.assertIsNotNone(cfg)

        fname = os.path.basename(cfg)
        self.assertEqual(fname, 'fetchdep.yml')

    def test_config_find_type02(self):
        prj_dir = fetch_unittest_assets_dir('cfgname-type02')
        self.assertTrue(os.path.isdir(prj_dir))

        cfg = find_configuration(prj_dir)
        self.assertIsNotNone(cfg)

        fname = os.path.basename(cfg)
        self.assertEqual(fname, '.fetchdep.yml')

    def test_config_find_type03(self):
        prj_dir = fetch_unittest_assets_dir('cfgname-type03')
        self.assertTrue(os.path.isdir(prj_dir))

        cfg = find_configuration(prj_dir)
        self.assertIsNotNone(cfg)

        fname = os.path.basename(cfg)
        self.assertEqual(fname, '.fetchdep')
