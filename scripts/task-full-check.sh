#!/usr/bin/env bash
#
# This is a helper script used to invoke all tests that should be passing
# for a changeset and required for a release.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)

cmd_prefix=
if command -v winpty >/dev/null 2>/dev/null; then
    cmd_prefix=winpty
fi

# invoke environments that can run with modern tox
primary_envs=(
    ruff
    pylint
    py37
    py38
    py39
    py310
    py311
    py312
    py313
    py314
    pypy3
    py37-extract-tests
    py38-extract-tests
    py39-extract-tests
    py310-extract-tests
    py311-extract-tests
    py312-extract-tests
    py313-extract-tests
    py314-extract-tests
    py37-release
    py38-release
    py39-release
    py310-release
    py311-release
    py312-release
    py313-release
    py314-release
)

envs=$(IFS=, ; echo "${primary_envs[*]}")
$cmd_prefix tox -p -e "$envs" "$@"

# invoke legacy environments with an older version of tox
legacy_envs=(
    py27
    py35
    py36
    pypy2
    py27-extract-tests
    py35-extract-tests
    py36-extract-tests
    py27-release
    py35-release
    py36-release
)

envs=$(IFS=, ; echo "${legacy_envs[*]}")
$cmd_prefix "$SHELL" \
    "$script_dir/tox-legacy.sh" \
    -p "$(nproc)" \
    -e "$envs" \
    --skip-missing-interpreters
