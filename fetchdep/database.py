# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from collections import OrderedDict


class ConfigDatabase:
    def __init__(self):
        """
        configuration database

        Tracks known dependencies determined from a configuration for
        individual project names.

        Attributes:
            db: the raw database
            tags: detected tags
        """
        self.db = OrderedDict()
        self.tags = set()

    def entries(self):
        """
        check if a project has been registered

        Args:
            name: the project name

        Returns:
            whether the project is registered
        """
        return list(self.db.keys())

    def exists(self, name):
        """
        check if a project has been registered

        Args:
            name: the project name

        Returns:
            whether the project is registered
        """
        return name in self.db

    def get(self, name):
        """
        return a dependency entry for a project

        Args:
            name: the project name

        Returns:
            the dependency
        """
        return self.db.get(name)

    def store(self, name, dependency):
        """
        track a dependency entry for a project

        Args:
            name: the project name
            dependency: the dependency
        """
        self.db[name] = dependency

    def track_tags(self, tags):
        """
        track known tags

        Args:
            tags: the tags
        """
        self.tags.update(tags)
