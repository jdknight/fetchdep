# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.defs import SiteVcsType
from fetchdep.util.io import resolve_dirname
from fetchdep.exceptions import InvalidNameConfigurationError
from fetchdep.exceptions import UnknownVcsTypeConfigurationError


class Dependency:
    def __init__(self, vcs, name, site, origin, tags=None):
        """
        a project dependency

        Holds the configuration state for identify a specific dependency
        for a project.

        Args:
            vcs: the vcs type
            name: the name of the dependency
            site: the site/source of the dependency
            origin: origin (configuration) of this dependency
            tags (optional): tags assocaited to this dependency

        Attributes:
            name: the name of the dependency
            origin: origin (configuration) of this dependency
            site: the site/source of the dependency
            tags: tags assocaited to this dependency
            vcs: the vcs type
        """
        self.name = name
        self.origin = origin
        self.site = site
        self.tags = tags.copy() if tags else set()
        self.vcs = vcs


def build_dependency(origin, name, site, tags=None):
    """
    build a dependency entry

    Helps build a dependency entry which can be used by fetchdep. This call
    uses the provided site to help determine the type of dependency, before
    building and returning it.

    Args:
        origin: the origin of this dependency
        name: the name of the dependency
        site: the site/source of the dependency
        tags (optional): tags assocaited to this dependency

    Returns:
        the built dependency

    Raises:
        InvalidNameConfigurationError: invalid name detected
        UnknownVcsTypeConfigurationError: unknown vcs detected
    """

    try:
        final_name = resolve_dirname(name)
    except ValueError:
        raise InvalidNameConfigurationError(origin, name)

    # determine the type of dependency this is
    final_site = site
    site_lc = site.lower()
    if site_lc.startswith('cvs+'):
        final_site = site[4:]
        vcs_type = SiteVcsType.CVS
    elif site_lc.startswith((
            ':ext:',
            ':extssh:',
            ':gserver:',
            ':kserver:',
            ':pserver:',
            )):
        vcs_type = SiteVcsType.CVS
    elif site_lc.startswith('git+'):
        final_site = site[4:]
        vcs_type = SiteVcsType.GIT
    elif site_lc.endswith('.git'):
        vcs_type = SiteVcsType.GIT
    elif site_lc.startswith('hg+'):
        final_site = site[3:]
        vcs_type = SiteVcsType.HG
    elif site_lc.startswith('mkdir'):
        vcs_type = SiteVcsType.MKDIR
    elif site_lc.startswith('svn+'):
        final_site = site[4:]
        vcs_type = SiteVcsType.SVN
    else:
        raise UnknownVcsTypeConfigurationError(origin, name, site)

    # build and return the dependency
    return Dependency(vcs_type, final_name, final_site, origin, tags=tags)
