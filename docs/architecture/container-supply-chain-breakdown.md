# Architecture Breakdown
## Verifiable Container Supply Chain for Secure Fraud Detection API

## I. System Context

Purpose of the service and why container provenance matters
in security-sensitive environments.

---

## II. High-Level Architecture

Overview of the pipeline:

Developer → CI → Container Build → Registry → Signing → Verification → SBOM

Reference diagram:
docs/diagrams/container-supply-chain-architecture.md

---

## III. Application Layer

FastAPI service structure
Health endpoint
Prediction endpoint
Audit logging

---

## IV. Container Runtime Design

Distroless runtime
Non-root execution
Minimal attack surface

---

## V. CI/CD Pipeline Architecture

GitHub Actions workflows

docker-smoke 
docker-smoke-readonly 
docker-perf-sanity 
docker-publish 
verify-signature 
release-sbom 

---

## VI. Supply Chain Security Model

Cosign keyless signing
OIDC identity verification
Digest-based verification

---

## VII. Dependency Transparency

SBOM generation with Syft
Artifact publication in CI

---

## VIII. Verification Workflow

How engineers independently verify the container artifact.

---

## IX. Design Tradeoffs

Why these tools were selected
What alternatives exist
