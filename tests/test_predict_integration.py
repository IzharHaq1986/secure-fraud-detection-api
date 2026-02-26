import os
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_predict_requires_api_key():
    response = client.post(
        "/v1/predict",
        json={
            "amount": 100.0,
            "currency": "USD",
            "merchant_country": "US",
            "channel": "web",
        },
    )
    assert response.status_code == 403


def test_predict_success_with_valid_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY_ADMIN", "test-key")

    response = client.post(
        "/v1/predict",
        headers={"X-API-Key": "test-key"},
        json={
            "amount": 100.0,
            "currency": "USD",
            "merchant_country": "US",
            "channel": "web",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "score" in body
    assert "decision" in body
