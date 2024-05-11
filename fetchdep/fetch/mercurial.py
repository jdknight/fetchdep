# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool.hg import HG
from fetchdep.util.log import err
from fetchdep.util.log import note


def fetch(opts):
    """
    support fetching from mercurial sources

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

    if not HG.exists():
        err('unable to fetch package; hg (mercurial) is not installed')
        return False

    note('fetching {}...', name)

    if not HG.execute(['--verbose', 'clone', site, target_dir]):
        err('unable to clone mercurial repository')
        return False

    return True
