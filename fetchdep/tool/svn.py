# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.tool import FetchdepTool

# executable used to run svn commands
SVN_COMMAND = 'svn'

# svn host tool helper
SVN = FetchdepTool(SVN_COMMAND)
