# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from collections import OrderedDict
from fetchdep.util.io import makedirs
from fetchdep.util.log import note
import os
import re


def fetch(opts):
    """
    test call to emulate fetching

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

    note('fetching {}...', name)

    # compile a list of dependencies to add (if any)
    dummy_dependencies = OrderedDict()
    entries = site.split()
    if len(entries) > 1:
        for entry in entries[1:]:
            sub_entry = re.sub(r'[^a-z:]', '', entry.lower())[:10]
            parts = sub_entry.split(':')
            name = parts[0]
            if name:
                dummy_dependencies[name] = parts[1] if len(parts) > 1 else ''

    if not makedirs(target_dir):
        return False

    if dummy_dependencies:
        cfg = os.path.join(target_dir, 'fetchdep.yml')
        with open(cfg, 'w') as f:
            f.write('fetchdep:\n')
            for name, extra in dummy_dependencies.items():
                f.write('  - name: fetchdep-{}\n'.format(name))
                f.write('    site: mkdir {}\n'.format(extra))

    return True
