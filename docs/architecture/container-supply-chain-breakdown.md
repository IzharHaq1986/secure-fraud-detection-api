# Architecture Breakdown
## Verifiable Container Supply Chain for Secure Fraud Detection API

## I. System Context

The Secure Fraud Detection API demonstrates how an API service can be deployed
with a verifiable container supply chain.

The goal of the system is not only to run a containerized FastAPI service but
also to ensure that the resulting container image can be independently verified.

The design focuses on three engineering goals:

• deterministic container builds 
• verifiable artifact provenance 
• transparent dependency visibility

These goals are implemented through a CI pipeline that builds the container,
signs the resulting image, and produces a Software Bill of Materials.

---

## II. High-Level Architecture

The container pipeline implemented in this repository follows a linear
verification model.

Developer → CI Pipeline → Container Build → Registry → Image Signing → Artifact Verification

The pipeline includes the following stages:

1. Source code commit triggers a GitHub Actions workflow.
2. The workflow builds a Distroless container image.
3. The image is pushed to GitHub Container Registry.
4. The image is signed using Cosign with GitHub OIDC identity.
5. The pipeline verifies the signature in CI.
6. A Software Bill of Materials is generated using Syft.

The architecture diagram below illustrates the flow.

See: `docs/diagrams/container-supply-chain-architecture.md`

---

## III. Application Layer

The application layer of the Secure Fraud Detection API is implemented using FastAPI.

The service is intentionally minimal because the primary focus of the project
is the container supply-chain pipeline rather than complex application logic.

The API currently exposes a small set of endpoints:

- `/health` — service health verification
- `/v1/predict` — fraud prediction endpoint

The application structure follows a modular layout.

Key architectural components include:

**Application Entry Point**

The FastAPI application instance is created in `main.py`, where middleware and
routers are registered.

**Authentication Layer**

API key authentication is implemented as a dependency, allowing protected
endpoints without tightly coupling authentication logic to route handlers.

**Security Middleware**

Middleware components provide:

- request identification
- rate limiting
- request validation

**Audit Logging**

Prediction decisions are recorded using tamper-evident logging. Each request
includes trace identifiers and model metadata to support later inspection.

This structure separates application logic from infrastructure concerns,
which allows the container pipeline and security mechanisms to evolve
independently of the API implementation.

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
