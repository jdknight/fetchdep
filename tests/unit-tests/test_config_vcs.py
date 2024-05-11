# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.config import Config
from fetchdep.defs import SiteVcsType
from fetchdep.exceptions import UnknownVcsTypeConfigurationError
from tests import FetchdepTestCase
from tests import fetch_unittest_assets_dir
import os


class TestConfigVcs(FetchdepTestCase):
    def test_config_vcs_cvs(self):
        expected = (
            SiteVcsType.CVS,
        )
        self._verify_type('vcs-cvs01', expected)
        self._verify_type('vcs-cvs02', expected)

    def test_config_vcs_git(self):
        expected = (
            SiteVcsType.GIT,
        )
        self._verify_type('vcs-git01', expected)
        self._verify_type('vcs-git02', expected)
        self._verify_type('vcs-git03', expected)

    def test_config_vcs_hg(self):
        expected = (
            SiteVcsType.HG,
        )
        self._verify_type('vcs-mercurial', expected)

    def test_config_vcs_multiple(self):
        expected = (
            SiteVcsType.CVS,
            SiteVcsType.GIT,
            SiteVcsType.HG,
            SiteVcsType.SVN,
        )
        self._verify_type('vcs-multiple', expected)

    def test_config_vcs_svn(self):
        expected = (
            SiteVcsType.SVN,
        )
        self._verify_type('vcs-svn', expected)

    def test_config_vcs_unknown(self):
        with self.assertRaises(UnknownVcsTypeConfigurationError):
            self._verify_type('vcs-unknown', (None,))

    def _verify_type(self, example, vcses):
        cfg_path = fetch_unittest_assets_dir(example, 'fetchdep.yml')
        self.assertTrue(os.path.exists(cfg_path))

        cfg = Config()
        loaded = cfg.load(cfg_path, expected=True)
        self.assertTrue(loaded)

        deps = cfg.extract()
        self.assertIsNotNone(deps)
        self.assertEqual(len(deps), len(vcses))

        for dependency, vcs in zip(deps, vcses):
            self.assertEqual(dependency.vcs, vcs)
