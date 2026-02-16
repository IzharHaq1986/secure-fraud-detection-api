#!/usr/bin/env bash
set -euo pipefail

# CI lock file verification.
# We ignore setuptools/wheel because GitHub runners may inject/update them.
# These are build tools and do not represent your application dependency graph.

LOCK_FILE="requirements.lock.txt"

if [[ ! -f "${LOCK_FILE}" ]]; then
  echo "ERROR: ${LOCK_FILE} is missing."
  echo "Create it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi

# Freeze current environment and remove build-tool noise.
python -m pip freeze --local \
  | grep -viE '^(setuptools|wheel)=='
  > /tmp/requirements.lock

# Apply the same normalization to the repo lock file.
grep -viE '^(setuptools|wheel)=='
  "${LOCK_FILE}" > /tmp/requirements.lock.expected

# Compare normalized lists.
if ! diff -u /tmp/requirements.lock.expected /tmp/requirements.lock; then
  echo ""
  echo "ERROR: ${LOCK_FILE} is out of date (ignoring setuptools/wheel)."
  echo "Update it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi
