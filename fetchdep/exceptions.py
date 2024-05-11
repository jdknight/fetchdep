# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

class FetchdepError(Exception):
    """
    base exception for all custom fetchdep exceptions
    """


class FetchdepMissingConfigurationError(FetchdepError):
    """
    exception thrown when missing a fetchdep configuration file
    """
    def __init__(self, path):
        super(FetchdepMissingConfigurationError, self).__init__('''\
missing configuration file

The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided configuration file path:

    {}
'''.strip().format(path))


class MissingNameConfigurationError(FetchdepError):
    """
    exception thrown when a dependency entry is missing a name value
    """
    def __init__(self, cfg):
        super(MissingNameConfigurationError, self).__init__('''\
missing configuration entry name

A configuration file defines a dependency entry without a name. Ensure each
dependency entry has a `name` option set.

  Configuration: {}
'''.strip().format(cfg))


class MissingSiteConfigurationError(FetchdepError):
    """
    exception thrown when a dependency entry is missing a site value
    """
    def __init__(self, cfg, name):
        super(MissingSiteConfigurationError, self).__init__('''\
missing configuration entry site

A configuration file defines a dependency entry without a site. Ensure each
dependency entry has a `site` option set.

  Configuration: {}
           Name: {}
'''.strip().format(cfg, name))


class InvalidNameConfigurationError(FetchdepError):
    """
    exception thrown when an unknown vcs type is detected
    """
    def __init__(self, cfg, name):
        super(InvalidNameConfigurationError, self).__init__('''\
unknown vcs type

A configuration file defines a dependency entry without a name. Ensure each
dependency entry has a `name` option set.
ue.

  Configuration: {}
           Name: {}
'''.strip().format(cfg, name))


class UnknownVcsTypeConfigurationError(FetchdepError):
    """
    exception thrown when an unknown vcs type is detected
    """
    def __init__(self, cfg, name, site):
        super(UnknownVcsTypeConfigurationError, self).__init__('''\
unknown vcs type

A configuration file defines a dependency which a VCS type cannot be
determined by its site value.

  Configuration: {}
           Name: {}
           Site: {}
'''.strip().format(cfg, name, site))
