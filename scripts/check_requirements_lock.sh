#!/usr/bin/env bash
set -euo pipefail

# CI lock file verification.
# Ensures requirements.lock.txt matches the environment installed in CI.

LOCK_FILE="requirements.lock.txt"

if [[ ! -f "${LOCK_FILE}" ]]; then
  echo "ERROR: ${LOCK_FILE} is missing."
  echo "Create it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi

python -m pip freeze --local > /tmp/requirements.lock

if ! diff -u "${LOCK_FILE}" /tmp/requirements.lock; then
  echo ""
  echo "ERROR: ${LOCK_FILE} is out of date."
  echo "Update it with: python -m pip freeze --local > ${LOCK_FILE}"
  exit 1
fi
