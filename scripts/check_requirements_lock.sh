#!/usr/bin/env bash
set -euo pipefail

# CI lock file verification (order-insensitive).
# We sort both files before diffing to avoid false failures caused by
# different freeze output ordering across environments.

LOCK_FILE="requirements.lock.txt"

if [[ ! -f "${LOCK_FILE}" ]]; then
  echo "ERROR: ${LOCK_FILE} is missing."
  echo "Create it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi

# Create a sorted view of the committed lock file.
sort "${LOCK_FILE}" > /tmp/requirements.lock.expected

# Freeze the current environment and sort it.
python -m pip freeze --local | sort > /tmp/requirements.lock.current

# Compare the sorted outputs.
if ! diff -u /tmp/requirements.lock.expected /tmp/requirements.lock.current; then
  echo ""
  echo "ERROR: ${LOCK_FILE} is out of date."
  echo "Update it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi
