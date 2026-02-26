# tests/test_health_endpoints.py
"""
Health endpoint contract tests.

Goal:
- Ensure health endpoints exist.
- Ensure they return HTTP 200.
- Ensure response structure remains stable.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_basic() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_health_details() -> None:
    response = client.get("/health/details")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_health_secure_details_requires_auth() -> None:
    # No API key provided
    response = client.get("/health/secure-details")
    assert response.status_code in (401, 403)
