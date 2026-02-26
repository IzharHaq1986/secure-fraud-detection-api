"""
runtime_info.py

Provides runtime metadata for diagnostics and operational visibility.
"""

import time
from dataclasses import dataclass
from typing import Dict

from app.model_loader import load_active_model

# Capture service start time once at import.
_SERVICE_START_TIME = time.time()


@dataclass(frozen=True)
class HealthDetails:
    """
    Structured health response model.
    """
    status: str
    uptime_seconds: float
    model_version: str


def get_health_details() -> Dict:
    """
    Return detailed service health information.

    - Ensures model artifact loads successfully.
    - Reports uptime.
    """
    model = load_active_model()

    uptime = time.time() - _SERVICE_START_TIME

    return {
        "status": "ok",
        "uptime_seconds": round(uptime, 2),
        "model_version": model.version
    }
