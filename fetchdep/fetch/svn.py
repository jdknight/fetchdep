# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool.svn import SVN
from fetchdep.util.log import err
from fetchdep.util.log import note


def fetch(opts):
    """
    support fetching from svn sources

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

    if not SVN.exists():
        err('unable to fetch package; svn is not installed')
        return False

    note('fetching {}...', name)

    if not SVN.execute(['checkout', site, target_dir]):
        err('unable to checkout module')
        return False

    return True
