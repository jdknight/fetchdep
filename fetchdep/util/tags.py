# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.compat import make_unicode
import re
import unicodedata


def resolve_tag(tag):
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

    if not tag:
        msg = 'empty tag'
        raise ValueError(msg)

    final_tag = tag.lower().strip()
    final_tag = make_unicode(final_tag)

    if not final_tag:
        msg = 'empty name after cleanup'
        raise ValueError(msg)

    # normalize a unicode name
    final_tag = unicodedata.normalize('NFKC', final_tag)

    # replace whitespaces with dashes
    cleaned_tag = re.sub(r'\s+', '', final_tag)
    if cleaned_tag != final_tag:
        msg = 'tag using invalid characters'
        raise ValueError(msg)

    return final_tag
