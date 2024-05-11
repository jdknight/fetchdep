# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

import sys

try:
    compat_input = raw_input
except NameError:
    compat_input = input  # pylint: disable=W0127


def make_unicode(value):
    """
    resolve a tag value

    Accepts a provided tag value which will be cleaned up to an expected
    value. An empty tag or invalid characters will trigger an exception.

    Args:
        tag: the raw tag value

    Returns:
        the final tag value

    Raises:
        ValueError: when an invalid tag is provided
    """

    if sys.version_info >= (3, 0):
        return value

    unicode_type = unicode  # noqa: F821  pylint: disable=E0602
    return value if isinstance(value, unicode_type) else value.decode('utf-8')
