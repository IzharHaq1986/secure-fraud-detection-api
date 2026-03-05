# Secure Fraud Detection API - Architecture Overview

## I. System Overview

The Secure Fraud Detection API demonstrates how an AI inference service can
be deployed with a hardened container supply chain and verifiable build
provenance.

The system combines:

• FastAPI application layer  
• Distroless container runtime  
• GitHub Actions CI/CD pipelines  
• Cosign container signing  
• SBOM generation using Syft

The goal is to provide a verifiable deployment pipeline suitable for
security-sensitive environments such as fintech platforms.

---

## II. Application Architecture

Core components:

FastAPI service
Model inference endpoint
Audit logging subsystem
Authentication middleware
Security middleware

The API exposes a simple health endpoint and a prediction endpoint used
for fraud detection inference.

---

## III. Container Architecture

The application is packaged using a multi-stage Docker build.

Runtime image:

gcr.io/distroless/python3-debian12:nonroot

Security properties:

Non-root execution  
Minimal attack surface  
No shell or package manager  
Explicit runtime dependencies

---

## IV. CI/CD Pipeline Architecture

GitHub Actions workflows implement a layered security pipeline.

Workflows:

docker-smoke.yml  
docker-smoke-readonly.yml  
docker-perf-sanity.yml  
docker-publish.yml  
verify-signature.yml  
release-sbom.yml  

Pipeline capabilities:

container build  
runtime validation  
container signing  
signature verification  
SBOM generation  

---

## V. Supply Chain Security

The repository demonstrates modern supply-chain security practices.

Controls implemented:

Cosign keyless signing via GitHub OIDC  
Digest-based image verification  
Immutable container tags  
SBOM generation using Syft

These controls allow engineers to independently verify artifact provenance.

---

## VI. Runtime Hardening

The container runtime environment enforces several restrictions:

read-only filesystem  
CPU limits  
memory limits  
PID limits  

These controls reduce the blast radius of potential runtime compromise.

---

## VII. Verification Workflow

Engineers can verify the container supply chain by:

1. Pulling the container image from GHCR
2. Verifying the Cosign signature
3. Inspecting the generated SBOM

This allows independent validation of the build pipeline and dependencies.

---

## VIII. Design Principles

The architecture prioritizes:

verifiability  
minimal attack surface  
deterministic builds  
transparent dependency tracking

The repository is structured as a client-facing reference implementation.
