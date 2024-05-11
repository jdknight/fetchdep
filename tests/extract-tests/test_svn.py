# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.io import execute
from tests import FetchdepExtractTestCase
from tests import interim_working_dir
from tests import prepare_testenv
import posixpath
import os


class TestToolSvn(FetchdepExtractTestCase):
    def test_svn(self):
        # prepare a svn repository
        self._svnadmin('create', self.repo_dir)

        # prepare the engine
        with prepare_testenv() as engine:
            # check if root directory is set
            work_dir = engine.opts.work_dir
            self.assertTrue(os.path.exists(work_dir))

            # svn requires posix path
            svn_path = '/' + self.repo_dir.replace(os.sep, posixpath.sep)

            # build a configuration which uses the generated repository
            cfg = os.path.join(work_dir, 'fetchdep.yml')
            with open(cfg, 'w') as f:
                f.write('fetchdep:\n')
                f.write('  - name: test\n')
                f.write('    site: svn+file://{}\n'.format(svn_path))

            # ensure the engine runs
            rv = engine.run()
            self.assertTrue(rv)

            # verify the project has be processed
            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), {'test'})

    def _svnadmin(self, *args):
        with interim_working_dir(self.repo_dir):
            out = []
            if execute(['svnadmin'] + list(args), capture=out) != 0:
                print(['svnadmin'] + list(args))
                print('\n'.join(out))
                msg = 'failed to issue svnadmin command'
                raise AssertionError(msg)
            return '\n'.join(out)
