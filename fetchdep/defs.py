# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.util.enum import Enum


# configuration key for the base yaml dictionary expected
CONFIG_BASE_KEY = 'fetchdep'

# configuration key for a dependency's name
CONFIG_NAME_KEY = 'name'

# configuration key for recursive flag associated to a dependency
CONFIG_RECURSIVE_KEY = 'recursive'

# configuration key for tags associated to a dependency
CONFIG_TAGS_KEY = 'tags'

# configuration key for the site value of a dependency
CONFIG_SITE_KEY = 'site'

# number of requests that can be processed before asking a user to continue
MAX_REQUEST_BEFORE_CONFIRM = 25

# list of support configuration names
SUPPORTED_CONFIG_NAMES = [
    '.fetchdep',
    '.fetchdep.yml',
    'fetchdep.yml',
]


class SiteVcsType(Enum):
    """
    site version control system types

    Defines supported version control system types for decided which fetching
    processing is used when acquiring resources.

    Attributes:
        CVS: concurrent versions system
        GIT: git
        HG: mercurial
        MKDIR: mkdir (for testing; undocumented)
        SVN: subversion
    """
    CVS = 'cvs'
    GIT = 'git'
    HG = 'hg'
    MKDIR = 'mkdir'
    SVN = 'svn'
