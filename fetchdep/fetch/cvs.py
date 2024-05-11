# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool.cvs import CVS
from fetchdep.util.io import makedirs
from fetchdep.util.log import err
from fetchdep.util.log import note
from fetchdep.util.log import verbose
import os


def fetch(opts):
    """
    support fetching from cvs sources

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

    if not CVS.exists():
        err('unable to fetch package; cvs is not installed')
        return False

    note('fetching {}...', name)

    try:
        cvsroot, module = site.rsplit(' ', 1)
    except ValueError:
        err('''\
improper cvs site defined

The provided CVS site does not define both the CVSROOT as well as the target
module to checkout. For example:

    :pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule

 Site: {}''', site)
        return False

    # cvs does not allow us to explicitly clone into a specific directory;
    # instead, adjust the working directory to where the folder will be held
    # and execute the checkout to specify the directory stem to use
    container_dir = os.path.dirname(target_dir)
    basename = os.path.basename(target_dir)

    # CVS requires the base directory exists before attempting to checkout
    verbose('preparing container directory')
    if not makedirs(container_dir):
        return False

    if not CVS.execute(['-d', cvsroot, 'checkout', '-d', basename, module],
            cwd=container_dir):
        err('unable to checkout module')
        return False

    return True
