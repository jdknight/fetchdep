# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from tests import FetchdepTestCase
from tests import run_testenv


class TestEngineRunRequired(FetchdepTestCase):
    def test_engine_run_required(self):
        config = {
            'required': True,
        }

        rv = run_testenv(config=config)
        self.assertFalse(rv)
