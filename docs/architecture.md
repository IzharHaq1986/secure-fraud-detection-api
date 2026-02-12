# Architecture (v1)

## High-level flow
Client -> Nginx (TLS) -> API (FastAPI) -> Model Inference -> Audit Logger -> Log Store

## Components
- Reverse proxy: Nginx terminating TLS
- API service: authentication, request validation, inference orchestration
- Model: local artifact loaded by API (versioned)
- Audit logging: append-only structured logs (JSON)
- Log store: local file for v1 (upgradable to database/central logging)

## Data boundaries
- Do not log raw sensitive payloads or PII.
- Log only:
  - request metadata (ids, role, timestamp)
  - model_version + schema version
  - decision + confidence scores
