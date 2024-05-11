# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from __future__ import unicode_literals
from fetchdep.config import Config
from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
from tests import prepare_testenv
import os


class TestTags(FetchdepTestCase):
    def test_tags_config(self):
        cfg_path = fetch_unittest_assets_dir('tags', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertTrue(loaded)

        deps = cfg.extract()
        self.assertIsNotNone(deps)
        self.assertEqual(len(deps), 4)

        entries = {}
        for dep in deps:
            entries[dep.name] = dep.tags.copy()

        example1_tags = entries.pop('example1')
        self.assertEqual(example1_tags, set())

        example2_tags = entries.pop('example2')
        self.assertEqual(example2_tags, {'tag1'})

        example3_tags = entries.pop('example3')
        self.assertEqual(example3_tags, {'tag2'})

        example4_tags = entries.pop('example4')
        self.assertEqual(example4_tags, {'tag1', 'tag2', 'tag3'})

    def test_tags_verify_loaded_all(self):
        expected = [
            'example1',
            'example2',
            'example3',
            'example4',
        ]

        cfg_path = fetch_unittest_assets_dir('tags', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'all_tags': True,
            'config': cfg_path,
            'state': True,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)

            entries = engine.cfgdb.entries()
            self.assertEqual(entries, expected)

    def test_tags_verify_loaded_default(self):
        tags = [
        ]

        expected_modules = [
            'example1',
        ]

        self._test_tags_verify_loaded(tags, expected_modules)

    def test_tags_verify_loaded_multiple(self):
        tags = {
            'tag1',
            'tag2',
        }

        expected_modules = [
            'example1',
            'example2',
            'example3',
            'example4',
        ]

        self._test_tags_verify_loaded(tags, expected_modules)

    def test_tags_verify_loaded_tag1(self):
        tags = {
            'tag1',
        }

        expected_modules = [
            'example1',
            'example2',
            'example4',
        ]

        self._test_tags_verify_loaded(tags, expected_modules)

    def test_tags_verify_loaded_tag2(self):
        tags = {
            'tag2',
        }

        expected_modules = [
            'example1',
            'example3',
            'example4',
        ]

        self._test_tags_verify_loaded(tags, expected_modules)

    def test_tags_verify_loaded_tag3(self):
        tags = {
            'tag3',
        }

        expected_modules = [
            'example1',
            'example4',
        ]

        self._test_tags_verify_loaded(tags, expected_modules)

    def _test_tags_verify_loaded(self, tags, expected):
        cfg_path = fetch_unittest_assets_dir('tags', 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        config = {
            'config': cfg_path,
            'state': True,
            'tag': tags,
        }

        with prepare_testenv(config=config) as engine:
            rv = engine.run()
            self.assertTrue(rv)

            entries = engine.cfgdb.entries()
            self.assertEqual(entries, expected)
