# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.io import execute
from fetchdep.util.io import makedirs
from tests import FetchdepExtractTestCase
from tests import generate_temp_dir
from tests import interim_working_dir
from tests import prepare_testenv
import os


# name to use for the cvs module
TEST_MODULE = 'module-test'


class TestToolCvs(FetchdepExtractTestCase):
    def test_cvs(self):
        # prepare a cvs repository
        with interim_working_dir(self.repo_dir):
            self._cvs('init')

        # build cvs module outside path, since linux-cvs will not be happy
        #  (Cannot check out files into the repository itself)
        with generate_temp_dir() as tmpdir, interim_working_dir(tmpdir):
            self._cvs('checkout', '.')
            makedirs(TEST_MODULE)
            self._cvs('add', TEST_MODULE)
            self._cvs('commit', '-m', 'test')

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
                f.write('    site: cvs+{} {}\n'.format(
                    self.repo_dir, TEST_MODULE))

            # ensure the engine runs
            rv = engine.run()
            self.assertTrue(rv)

            # verify the project has be processed
            entries = engine.cfgdb.entries()
            self.assertEqual(set(entries), {'test'})

    def _cvs(self, *args):
        # configure CVSROOT to the repository
        new_args = ('-d', self.repo_dir) + args

        out = []
        if execute(['cvs'] + list(new_args), capture=out) != 0:
            print(['cvs'] + list(new_args))
            print('\n'.join(out))
            msg = 'failed to issue cvs command'
            raise AssertionError(msg)
        return '\n'.join(out)
