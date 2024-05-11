# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool import FetchdepTool

# executable used to run git commands
GIT_COMMAND = 'git'

# list of environment keys to filter from a environment dictionary
GIT_SANITIZE_ENV_KEYS = [
    # disable repository location overrides
    'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_DIR',
    'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY',
    'GIT_WORK_TREE',
]

# git host tool helper
GIT = FetchdepTool(GIT_COMMAND, env_sanitize=GIT_SANITIZE_ENV_KEYS)
