# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import prepare_testenv
import os


class TestEngineRunEnvironConfig(FetchdepTestCase):
    def test_engine_run_environ_cfg_debug(self):
        os.environ['FETCHDEP_DEBUG'] = '1'

        with prepare_testenv() as engine:
            self.assertTrue(engine.opts.debug)
            self.assertTrue(engine.opts.verbose)

    def test_engine_run_environ_cfg_verbose(self):
        os.environ['FETCHDEP_VERBOSE'] = '1'

        with prepare_testenv() as engine:
            self.assertFalse(engine.opts.debug)
            self.assertTrue(engine.opts.verbose)
