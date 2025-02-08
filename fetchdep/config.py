# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.defs import CONFIG_BASE_KEY
from fetchdep.defs import CONFIG_NAME_KEY
from fetchdep.defs import CONFIG_RECURSIVE_KEY
from fetchdep.defs import CONFIG_SITE_KEY
from fetchdep.defs import CONFIG_TAGS_KEY
from fetchdep.defs import SUPPORTED_CONFIG_NAMES
from fetchdep.dependency import build_dependency
from fetchdep.exceptions import MissingNameConfigurationError
from fetchdep.exceptions import MissingSiteConfigurationError
from fetchdep.util.compat import make_unicode
from fetchdep.util.log import err
from fetchdep.util.log import verbose
from fetchdep.util.tags import resolve_tag
from io import open  # noqa: A004
import os
import yaml

try:
    FileNotFoundError  # noqa: B018  pylint: disable=E0601
except NameError:
    FileNotFoundError = IOError  # noqa: A001


class Config:
    def __init__(self):
        """
        configuration instance

        Holds the extracted configuration information from a fetchdep YAML
        file.
        """
        self.config = {}
        self.path = None

    def load(self, path, expected=False):
        """
        load configuration information from a provided file

        This call will open a YAML configuration file and populate various
        configuration options.

        Args:
            path: the path of the configuration file to load
            expected (optional): whether the provided path is expected to load

        Returns:
            whether a file was loaded
        """

        self.path = path

        try:
            verbose('attempting to load configuration file: {}', path)
            with open(path, encoding='utf_8') as f:
                try:
                    raw_config = yaml.safe_load(f)
                    if CONFIG_BASE_KEY in raw_config:
                        self.config = raw_config[CONFIG_BASE_KEY]
                        return True

                    err('invalid fetchdep configuration: {}', path)
                except yaml.YAMLError as e:
                    err('unable to load configuration file: {}', path)
                    err(e)
        except FileNotFoundError:
            if expected:
                err('configuration file does not exist: {}', path)
        except OSError as e:
            err('unable to load configuration file: {}', path)
            err(e)

        return not expected

    def extract(self):
        deps = []

        for entry in self.config:
            name = entry.get(CONFIG_NAME_KEY)
            site = entry.get(CONFIG_SITE_KEY)
            raw_tags = entry.get(CONFIG_TAGS_KEY)
            recursive = entry.get(CONFIG_RECURSIVE_KEY, True)

            if not name:
                raise MissingNameConfigurationError(self.path)

            if not site:
                raise MissingSiteConfigurationError(self.path, name)

            name = make_unicode(name)
            site = make_unicode(site)

            tags = set()
            if raw_tags:
                for raw_tag in raw_tags:
                    tag = resolve_tag(raw_tag)
                    tags.add(tag)

            dep = build_dependency(self.path, name, site,
                tags=tags, recursive=recursive)
            deps.append(dep)

        return deps


def find_configuration(path):
    """
    find a configuration in a provided path

    This call can be used to find an expected fetchdep configuration file
    in a provided path (of known default names). If no configuration file
    can be found, this call will return ``None``.

    Args:
        path: the path to search

    Returns:
        the configuration filename; otherwise ``None``
    """

    for fname in SUPPORTED_CONFIG_NAMES:
        cfg_file = os.path.join(path, fname)
        if os.path.isfile(cfg_file):
            return cfg_file

    return None
