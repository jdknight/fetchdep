# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

try:
    basestring  # noqa: B018  pylint: disable=E0601
except NameError:
    basestring = str

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence  # pylint: disable=W1512


def is_sequence_not_string(obj):
    """
    return whether or not the provided object is a non-string sequence

    Returns ``True`` if the provided ``obj`` is a sequence type but is also not
    a string; ``False`` otherwise.

    Args:
        obj: the object to interpret

    Returns:
        whether or not a non-string sequence
    """
    return isinstance(obj, Sequence) and not isinstance(obj, basestring)
