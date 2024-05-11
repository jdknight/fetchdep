# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from __future__ import unicode_literals
from tests import FetchdepTestCase
from fetchdep.util.io import resolve_dirname


class TestUtilIoResolveDirname(FetchdepTestCase):
    def test_util_io_resolve_valid(self):
        resolved = resolve_dirname('example-name')
        self.assertEqual(resolved, 'example-name')

        resolved = resolve_dirname(' test ')
        self.assertEqual(resolved, 'test')

        resolved = resolve_dirname('prüfen')
        self.assertEqual(resolved, 'prüfen')

    def test_util_io_resolve_dirname_empty(self):
        with self.assertRaises(ValueError):
            resolve_dirname(None)

        with self.assertRaises(ValueError):
            resolve_dirname('')

        with self.assertRaises(ValueError):
            resolve_dirname(' ')

    def test_util_io_resolve_dirname_invalid_chars(self):
        with self.assertRaises(ValueError):
            resolve_dirname('test?')

        with self.assertRaises(ValueError):
            resolve_dirname('*another-test*')

        with self.assertRaises(ValueError):
            resolve_dirname('sub/path')

    def test_util_io_resolve_dirname_restricted(self):
        with self.assertRaises(ValueError):
            resolve_dirname('COM2')

        with self.assertRaises(ValueError):
            resolve_dirname('NUL')
