from fastapi import FastAPI, Header
from pydantic import BaseModel
import uuid
from typing import Any, Dict
from dotenv import load_dotenv
from fastapi import Request
from app.model_loader import load_active_model

from app.audit_logger import write_audit_event
from app.auth import authenticate
from app.middleware import RequestIdMiddleware, SecurityHeadersMiddleware, SimpleRateLimitMiddleware

# Load environment variables from .env (if present).
# .env is excluded by .gitignore and must never be committed.
load_dotenv()

app = FastAPI(title="Secure Fraud Detection API")
# Middleware order matters:
# - RequestId first: so everything downstream can use request.state.request_id
# - Rate limiting early: protect API from abuse
# - Security headers last: decorate responses
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, max_requests=60, window_seconds=60)
app.add_middleware(SecurityHeadersMiddleware)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}


@app.post("/v1/predict")
def predict(request: Request, payload: Dict[str, Any], x_api_key: str | None = Header(default=None, alias="X-API-Key")):

    """
    Fraud prediction endpoint (v1) with API-key auth.

    - Rejects requests missing/invalid keys.
    - Writes audit events including caller role.
    """
    caller = authenticate(x_api_key)
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    model = load_active_model()
    model_version = model.version

    prediction = "not_implemented"
    confidence = 0.0

    response = {
        "request_id": request_id,
        "model_version": model_version,
        "prediction": prediction,
        "confidence": confidence
    }

    # Audit event includes role and key_id (non-sensitive).
    audit_event = {
        "event_type": "model_inference",
        "request_id": request_id,
        "caller_role": caller.role,
        "caller_key_id": caller.key_id,
        "model_version": model_version,
        "prediction": prediction,
        "confidence": confidence
    }

    write_audit_event(audit_event)

    return response
