# tests/test_openapi_contract.py
"""
OpenAPI contract integrity test.

FastAPI often uses $ref pointers for schemas:
- responses may reference components via "$ref"
This test resolves $ref so we can assert on actual properties.
"""

from __future__ import annotations

from app.main import app


def _resolve_schema_ref(openapi: dict, schema: dict) -> dict:
    """
    Resolve an OpenAPI schema object that may contain a $ref.

    This is a small helper so our test stays robust even when FastAPI
    chooses to inline schemas vs reference components.
    """

    ref = schema.get("$ref")
    if not ref:
        return schema

    # Example: "#/components/schemas/FraudResponse"
    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        raise AssertionError(f"Unexpected $ref format: {ref}")

    name = ref[len(prefix):]
    return openapi["components"]["schemas"][name]


def test_openapi_predict_contract() -> None:
    openapi = app.openapi()

    # Ensure the path exists
    assert "/v1/predict" in openapi["paths"]

    # Ensure POST method exists
    assert "post" in openapi["paths"]["/v1/predict"]

    post_spec = openapi["paths"]["/v1/predict"]["post"]

    # Ensure request body schema exists
    assert "requestBody" in post_spec

    # Ensure response schema exists
    assert "responses" in post_spec
    assert "200" in post_spec["responses"]
    
    # Health endpoints must exist (monitoring/load balancer contract)
    assert "/health" in openapi["paths"]
    assert "get" in openapi["paths"]["/health"]

    assert "/health/details" in openapi["paths"]
    assert "get" in openapi["paths"]["/health/details"]

    assert "/health/secure-details" in openapi["paths"]
    assert "get" in openapi["paths"]["/health/secure-details"]

    response_schema = post_spec["responses"]["200"]["content"]["application/json"]["schema"]
    resolved = _resolve_schema_ref(openapi, response_schema)

    # Basic shape validation
    assert "properties" in resolved

    props = resolved["properties"]
    assert "request_id" in props
    assert "score" in props
    assert "decision" in props
