# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.io import execute
from tests import FetchdepExtractTestCase
from tests import interim_working_dir
from tests import prepare_testenv
import os


class TestToolMercurial(FetchdepExtractTestCase):
    def test_mercurial(self):
        # prepare a mercurial repository
        self._hg('init', self.repo_dir)
        self._create_commit('initial commit')

        # prepare the engine
        with prepare_testenv() as engine:
            # check if root directory is set
            work_dir = engine.opts.work_dir
            self.assertTrue(os.path.exists(work_dir))

            # build a configuration which uses the generated repository
            cfg = os.path.join(work_dir, 'fetchdep.yml')
            with open(cfg, 'w') as f:
                f.write('fetchdep:\n')
                f.write('  - name: test\n')
                f.write('    site: hg+{}\n'.format(self.repo_dir))

            # ensure the engine runs
            rv = engine.run()
            self.assertTrue(rv)

            # verify the project has be processed
            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), {'test'})

    def _hg(self, *args):
        with interim_working_dir(self.repo_dir):
            out = []
            if execute(['hg', '--noninteractive'] + list(args),
                    capture=out) != 0:
                print(['hg'] + list(args))
                print('\n'.join(out))
                msg = 'failed to issue hg command'
                raise AssertionError(msg)
            return '\n'.join(out)

    def _create_commit(self, msg='test'):
        # Mercurial requires some content on new repos; add a dummy file
        # for new repositories.
        try:
            dummy_file = os.path.join(self.repo_dir, 'dummy')
            with open(dummy_file, 'ab'):
                pass
        except OSError:
            pass

        self._hg('add', '.')
        self._hg('commit', '-m', msg)
