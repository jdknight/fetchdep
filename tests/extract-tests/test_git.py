# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.io import execute
from tests import FetchdepExtractTestCase
from tests import interim_working_dir
from tests import prepare_testenv
import os


class TestToolGit(FetchdepExtractTestCase):
    def test_git(self):
        # prepare a git repository
        self._git('init', self.repo_dir)
        self._git('checkout', '-B', 'test')
        self._git('config', 'user.email', 'test@example.com')
        self._git('config', 'user.name', 'Unit Test')
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
                f.write('    site: git+file://{}\n'.format(self.repo_dir))

            # ensure the engine runs
            rv = engine.run()
            self.assertTrue(rv)

            # verify the project has be processed
            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), {'test'})

    def _git(self, *args):
        with interim_working_dir(self.repo_dir):
            out = []
            if execute(['git'] + list(args), capture=out) != 0:
                print(['git'] + list(args))
                print('\n'.join(out))
                msg = 'failed to issue git command'
                raise AssertionError(msg)
            return '\n'.join(out)

    def _create_commit(self, msg='test'):
        self._git('commit', '--allow-empty', '-m', msg)
        return self._git('rev-parse', 'HEAD')
