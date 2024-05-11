# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool import FetchdepTool

# executable used to run mercurial commands
HG_COMMAND = 'hg'

# dictionary of environment entries append to the environment dictionary
HG_EXTEND_ENV = {
    # hg is most likely a python script; ensure output is unbuffered
    'PYTHONUNBUFFERED': '1',
}

# mercurial host tool helper
HG = FetchdepTool(HG_COMMAND, env_include=HG_EXTEND_ENV)
