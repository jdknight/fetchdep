# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool import FetchdepTool

# executable used to run cvs commands
CVS_COMMAND = 'cvs'

# list of environment keys to filter from a environment dictionary
CVS_SANITIZE_ENV_KEYS = [
    'CVSIGNORE',
    'CVSREAD',
    'CVSUMASK',
    'CVSWRAPPERS',
    'CVS_SERVER',
]

# cvs host tool helper
CVS = FetchdepTool(CVS_COMMAND, env_sanitize=CVS_SANITIZE_ENV_KEYS)
