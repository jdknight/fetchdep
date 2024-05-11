# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool.git import GIT
from fetchdep.util.log import err
from fetchdep.util.log import note


def fetch(opts):
    """
    support fetching from git sources

    With provided fetch options (``FetchOptions``), the fetch stage
    will be processed.

    Args:
        opts: fetch options

    Returns:
        ``True`` if the fetch stage is completed; ``False`` otherwise
    """

    assert opts
    name = opts.name
    site = opts.site
    target_dir = opts.target_dir

    if not GIT.exists():
        err('unable to fetch package; git is not installed')
        return None

    note('fetching {}...', name)

    if not GIT.execute(['clone', site, '--progress', target_dir]):
        err('unable to clone git repository')
        return False

    return True
