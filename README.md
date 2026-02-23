[CI](https://github.com/IzharHaq1986/secure-fraud-detection-api/actions/workflows/ci.yml/badge.svg)[(https://github.com/IzharHaq1986/secure-fraud-detection-api/actions/workflows/ci.yml)]

<!-- Tech Stack Badges -->
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-ff69b4)
![Ruff](https://img.shields.io/badge/Linter-Ruff-000000)
![pytest](https://img.shields.io/badge/Tests-pytest-blueviolet)
![Coverage](https://img.shields.io/badge/Coverage-85%25+-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Ubuntu_22.04-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Secure Fraud Detection API (Fintech)

Security-first fraud detection API for fintech startups. Demonstrates audit-grade logging, threat modeling, RBAC, TLS-secured deployment on Ubuntu, and compliance-aligned AI architecture.

## What this repo proves
- Secure API design for model inference
- Audit-ready decision logging (trace IDs, model versioning)
- Threat modeling and risk-driven mitigations
- Ubuntu-based deployment with TLS and hardened defaults

## Docs
- docs/scope.md
- docs/architecture.md
- docs/threat_model.md
- docs/risk_matrix.md

## Project Structure

```text
secure-fraud-detection-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory + router registration
│   ├── auth.py                 # API-key authentication dependency
│   ├── schemas.py              # Pydantic request/response models
│   ├── routes/
│   │   └── predict.py          # /v1/predict endpoint (single source of truth)
│   ├── middleware.py           # Security / rate limiting / request-id middleware
│   ├── audit_logger.py         # Tamper-evident audit logging
│   └── model_loader.py         # Model artifact loading & validation
│
├── tests/
│   ├── conftest.py             # Test bootstrap + deterministic env setup
│   ├── test_predict.py         # API behavior tests
│   └── test_routes_unique.py   # Prevent duplicate route registration
│
├── scripts/
│   └── check_requirements_lock.sh  # CI lock verification script
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Main CI pipeline
│   │   └── release-sbom.yml    # SBOM generation on version tags
│   └── dependabot.yml          # Automated dependency updates
│
├── requirements.txt            # Direct dependencies (human-curated)
├── requirements.lock.txt       # Fully pinned environment (CI reproducible)
└── README.md
```

## Release process (tags + SBOM)
This repository uses semantic version tags to create versioned releases and attach an SBOM.

### Create a release tag
```bash
# Example: bump MINOR for backward-compatible improvements
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```bash 
