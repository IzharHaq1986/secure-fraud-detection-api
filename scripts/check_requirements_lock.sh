#!/usr/bin/env bash
set -euo pipefail

# CI lock file verification.
# We compare requirements.lock.txt to the installed environment, but ignore
# build-tooling packages that GitHub runners may inject or update:
# - setuptools
# - wheel
#
# These do not affect your application runtime behavior and are not worth
# failing CI over.

LOCK_FILE="requirements.lock.txt"

if [[ ! -f "${LOCK_FILE}" ]]; then
  echo "ERROR: ${LOCK_FILE} is missing."
  echo "Create it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi

# Generate a normalized lock from the current environment.
python -m pip freeze --local \
  | grep -viE '^(setuptools|wheel)=='
  > /tmp/requirements.lock

# Normalize the repo lock file the same way before diffing.
grep -viE '^(setuptools|wheel)=='
  "${LOCK_FILE}" > /tmp/requirements.lock.expected

if ! diff -u /tmp/requirements.lock.expected /tmp/requirements.lock; then
  echo ""
  echo "ERROR: ${LOCK_FILE} is out of date (ignoring setuptools/wheel)."
  echo "Update it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi
