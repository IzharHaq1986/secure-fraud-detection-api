#!/usr/bin/env bash
set -euo pipefail

# CI lock file verification.
# We compare requirements.lock.txt to the installed environment.
# We ignore build-tool packages injected by CI:
#   - setuptools
#   - wheel
#
# We also sort both files before diffing to avoid order-related noise.

LOCK_FILE="requirements.lock.txt"

if [[ ! -f "${LOCK_FILE}" ]]; then
  echo "ERROR: ${LOCK_FILE} is missing."
  echo "Create it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi

# Normalize CI environment freeze:
python -m pip freeze --local \
  | grep -viE '^(setuptools|wheel)=='
  | sort > /tmp/requirements.lock.current

# Normalize repository lock file:
grep -viE '^(setuptools|wheel)=='
  "${LOCK_FILE}" \
  | sort > /tmp/requirements.lock.expected

# Compare normalized results:
if ! diff -u /tmp/requirements.lock.expected /tmp/requirements.lock.current; then
  echo ""
  echo "ERROR: ${LOCK_FILE} is out of date (ignoring setuptools/wheel)."
  echo "Update it with:"
  echo "  python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi
