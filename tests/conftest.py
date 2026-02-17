# tests/conftest.py
"""
Pytest bootstrap.

Ensures the project root is on sys.path so imports like `from app.main import app`
work when running `pytest` from the repo root.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
