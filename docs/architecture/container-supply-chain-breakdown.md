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
