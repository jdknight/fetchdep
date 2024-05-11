# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from __future__ import unicode_literals
from tests import FetchdepTestCase
from fetchdep.util.tags import resolve_tag


class TestUtilIoResolveDirname(FetchdepTestCase):
    def test_util_tag_resolve_valid(self):
        resolved = resolve_tag('example-tag')
        self.assertEqual(resolved, 'example-tag')

        resolved = resolve_tag(' test ')
        self.assertEqual(resolved, 'test')

        resolved = resolve_tag('prüfen')
        self.assertEqual(resolved, 'prüfen')

    def test_util_tag_resolve_dirname_empty(self):
        with self.assertRaises(ValueError):
            resolve_tag(None)

        with self.assertRaises(ValueError):
            resolve_tag('')

        with self.assertRaises(ValueError):
            resolve_tag(' ')

    def test_util_tag_resolve_dirname_invalid_chars(self):
        with self.assertRaises(ValueError):
            resolve_tag('another test')
