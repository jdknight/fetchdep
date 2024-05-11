# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.defs import SiteVcsType
from fetchdep.fetch.cvs import fetch as fetch_cvs
from fetchdep.fetch.git import fetch as fetch_git
from fetchdep.fetch.mercurial import fetch as fetch_mercurial
from fetchdep.fetch.mkdir import fetch as fetch_mkdir
from fetchdep.fetch.svn import fetch as fetch_svn
from fetchdep.util.log import err
import os


class FetchOptions:
    """
    fetch-type options

    Provides a series of options from the fetchdep process into a fetch-type
    handler. A handler's ``fetch`` method will be passed options to react on.

    Attributes:
        ext: extension (pass-through) options
        name: the name of the dependency being processed
        site: the site (uri) to acquire a dependency's resources
        target_dir: directory to store fetched content
    """
    def __init__(self):
        self.ext = {}
        self.name = None
        self.site = None
        self.target_dir = None


class FetchRequest:
    def __init__(self, fetcher, dep, target_dir):
        self.fetcher = fetcher
        self.dep = dep
        self.target_dir = target_dir


def prepare_fetch_request(dep, opts):

    # find fetching method for the target vcs-type
    fetcher = None
    if dep.vcs == SiteVcsType.CVS:
        fetcher = fetch_cvs
    elif dep.vcs == SiteVcsType.GIT:
        fetcher = fetch_git
    elif dep.vcs == SiteVcsType.HG:
        fetcher = fetch_mercurial
    elif dep.vcs == SiteVcsType.MKDIR:
        fetcher = fetch_mkdir
    elif dep.vcs == SiteVcsType.SVN:
        fetcher = fetch_svn

    if not fetcher:
        err('fetch type is not implemented: {}', dep.vcs)
        return None

    target_dir = os.path.join(opts.work_dir, dep.name)

    return FetchRequest(fetcher, dep, target_dir)
