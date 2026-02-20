# tests/conftest.py
"""
Pytest bootstrap and test-environment configuration.

What this file does:
1) Ensures the repository root is on sys.path so imports like:
      from app.main import app
   work reliably in local runs and CI.

2) Provides deterministic API-key environment variables for tests.
   This avoids relying on a local .env file (which CI does not load).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the repo root is importable
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    # Put project root first so local imports win over any similarly named packages.
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Ensure API-key auth has known values during tests
# ---------------------------------------------------------------------------

# These values MUST match what your tests use in VALID_HEADERS in tests/test_predict.py.
os.environ.setdefault("API_KEY_ADMIN", "admin-secret-123")
os.environ.setdefault("API_KEY_SERVICE", "service-secret-123")
