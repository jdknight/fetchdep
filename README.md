# fetchdep

[![pip Version](https://badgen.net/pypi/v/fetchdep?label=PyPI)](https://pypi.python.org/pypi/fetchdep)
[![Supports Various Python versions](https://badgen.net/static/Python/2.7%20%7C%203.5-3.13)](https://pypi.python.org/pypi/fetchdep)
[![Build Status](https://github.com/jdknight/fetchdep/actions/workflows/build.yml/badge.svg)](https://github.com/jdknight/fetchdep/actions/workflows/build.yml)

## Overview

The fetchdep utility provides an easy way for developers to fetch dependencies
for software projects that work under a container path. If a project contains
a fetchdep configuration at its root, a user can invoke `fetchdep` to
automatically download sources alongside the working path of a project. This
can be useful for projects which may not have package management capabilities.

The following version control systems are supported:
CVS, Git, Mercurial, SVN.

## Requirements

* [Python][python] 2.7 or 3.5+
* [PyYAML][pyyaml]
* *(optional)* [CVS][cvs]
* *(optional)* [Git][git]
* *(optional)* [Mercurial][hg]
* *(optional)* [SVN][svn]

## Installation

This tool can be installed using [pip][pip] or [pipx][pipx]:

```shell
pipx install fetchdep
 (or)
pip install fetchdep
 (or)
python -m pip install fetchdep
```

## Usage

This tool can be invoked from a command line using:

```shell
fetchdep --help
 (or)
python -m fetchdep --help
```

## Examples

Consider a project that is cloned in the following path:

```
└── ~/workdir
    └── my-awesome-project/
        └── fetchdep.yml
```

If a user is working inside the project directory and invokes `fetchdep`:

```
$ cd workdir/my-awesome-project
$ fetchdep
```

This can automatically clone dependencies alongside the project as follows:

```
└── ~/workdir
    ├── my-awesome-library-a/
    |   └── ...
    ├── my-awesome-library-b/
    |   └── ...
    ├── my-awesome-library-c/
    |   └── ...
    └── my-awesome-project/
        └── fetchdep.yml
```

## Configuration

A fetchdep configuration file can be named either one of the following:

- `fetchdep.yml`
- `.fetchdep.yml`
- `.fetchdep`

Configuration files are YAML defined configurations. Each configuration is
expected to have a root `fetchdep` list, which holds one or more dependencies
to be fetched. For example:

```yml
fetchdep:
  # cvs
  - name: my-module-a
    site: :pserver:anonymous@cvs.example.org:/cvsroot/my-module-a my-module-a
  # git
  - name: my-module-b
    site: https://example.com/myteam/my-module-b.git
  # hg
  - name: my-module-c
    site: hg+https://www.example.org/repo/my-module-c
  # svn
  - name: my-module-d
    site: svn+https://svn.code.example.com/c/myteam/my-module-d/trunk
```

- Each entry must have a `name`, which will be used for the folder name to
  checkout sources to.
- Each entry must also have a `site`, defining what type of source will be
  fetched. Accepted site prefixes include `cvs+`, `git+`, `hg+` and `svn+`.
  Although, some sites may omit the prefix if this utility can determine
  what type of sources are being fetched.

## Capabilities

### Tags

This utility supports tagged dependencies. A project can define one or more
tags for a project. For example:

```yml
fetchdep:
  - name: my-test-module
    site: https://example.com/myteam/my-test-module.git
    tags:
      - test
```

By default, if a user invokes `fetchdep` with no other arguments, the
`my-test-module` module above will not be fetched. To include sources which
have a tag assigned, the tag must be added to the command line:

```
fetchdep --tag test
```

Multiple tags can be added by repeating the `--tag` argument. Users can also
use the `--all-tags` argument to fetch every dependency.

### Recursive

The fetchdep utility will fetch only the current project's defined
dependencies. If a project dependency defines their own fetchdep configuration,
additional dependencies will not be fetched by default.

To support downloading a project's dependency's dependencies, the `--recursive`
option can be used:

```
fetchdep --recursive
```

Fetching too many projects may cause fetchdep to prompt to continue. This can
be overridden using the `-y` argument.

### Dry-run

Users can always invoke with the `--dry-run` argument to inspect which
dependencies will be fetched without invoking a fetch operation.


[cvs]: https://cvs.nongnu.org/
[git]: https://git-scm.com/
[hg]: https://www.mercurial-scm.org/
[pip]: https://pip.pypa.io/
[pipx]: https://pipx.pypa.io/
[python]: https://www.python.org/
[pyyaml]: https://pyyaml.org/
[svn]: https://subversion.apache.org/
