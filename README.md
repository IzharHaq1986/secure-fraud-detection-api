[![CI](https://github.com/IzharHaq1986/secure-fraud-detection-api/actions/workflows/ci.yml/badge.svg)](https://github.com/IzharHaq1986/secure-fraud-detection-api/actions/workflows/ci.yml)

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

## Release process (tags + SBOM)

This repository uses semantic version tags to create versioned releases and attach an SBOM.

### Create a release tag
```bash
# Example: bump MINOR for backward-compatible improvements
git tag -a v1.0.0 -m "Release v1.1.0"
git push origin v1.1.0
