# tests/test_routes_unique.py
"""
Route registry tests.

Goal:
- Ensure we never accidentally register duplicate endpoints.
- Specifically: there must be exactly one POST /v1/predict.
"""

from app.main import app


def test_only_one_predict_route_exists():
    """
    There must be exactly one POST /v1/predict route.

    Duplicate registrations can cause security drift (auth bypass),
    inconsistent responses, and unstable CI behavior.
    """

    matches = [
        route
        for route in app.routes
        if getattr(route, "path", None) == "/v1/predict"
        and "POST" in getattr(route, "methods", set())
    ]

    assert len(matches) == 1, f"Expected 1 POST /v1/predict, found {len(matches)}"
