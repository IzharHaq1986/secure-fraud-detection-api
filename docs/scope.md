# Scope (v1)

## In scope
- One prediction endpoint: `POST /v1/predict`
- Authentication (API key or JWT) + basic RBAC roles
- Audit-grade logging:
  - request_id / trace_id
  - caller identity (non-PII identifier)
  - model_version + feature schema version
  - decision output + timestamp
- Secure Ubuntu deployment:
  - TLS termination (Nginx) in front of API
  - secrets stored outside source control
- Reproducible local run + deploy steps

## Out of scope (v1)
- UI / dashboards
- Real bank integrations
- Real PII datasets
- Claims of certification or regulatory approval

## Definition of done
- Runs on Ubuntu from documented steps
- Auth enforced on prediction endpoint
- Audit logs produced and verifiable
- Threat model + risk matrix present and referenced
- Model inference reproducible with a pinned model artifact
