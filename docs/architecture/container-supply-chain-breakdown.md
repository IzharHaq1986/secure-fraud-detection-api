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

The Secure Fraud Detection API runs inside a hardened container environment.

The runtime container uses the following base image:

gcr.io/distroless/python3-debian12:nonroot

Distroless images intentionally remove components that are commonly present
in standard container images. These images do not include:

- shell utilities
- package managers
- unnecessary system libraries

Reducing the number of installed components decreases the potential attack
surface of the running container.

### Non-Root Execution

The container runs as a non-root user by default. Running services as root
inside containers increases the risk of privilege escalation if a runtime
vulnerability is exploited.

Using the nonroot variant of the Distroless image ensures the service
runs with minimal privileges.

### Runtime Constraints

The CI pipeline validates several runtime restrictions:

- read-only filesystem
- CPU limits
- memory limits
- PID limits

These restrictions reduce the blast radius of potential runtime compromise.

### Separation of Build and Runtime Stages

The Dockerfile uses a multi-stage build process.

The build stage installs dependencies and prepares the application
environment. The runtime stage contains only the files required to
execute the service.

This separation helps ensure that development tools and temporary
build artifacts do not appear in the final container image.

---

## V. CI/CD Pipeline Architecture

The Secure Fraud Detection API uses GitHub Actions to implement a
multi-stage CI/CD pipeline that builds, validates, signs, and documents
the container artifact.

The workflows are intentionally separated into small, focused stages.
This makes it easier to reason about the pipeline and identify failures.

### Pipeline Overview

The CI/CD process includes the following stages:

1. Source code commit triggers the CI pipeline.
2. The container image is built from the Dockerfile.
3. Runtime validation checks confirm container restrictions.
4. The container image is pushed to GitHub Container Registry (GHCR).
5. The image is signed using Cosign with GitHub OIDC identity.
6. The pipeline verifies the signature.
7. A Software Bill of Materials is generated.

### Workflow Structure

The repository contains several dedicated workflows:

- docker-smoke.yml
- docker-smoke-readonly.yml
- docker-perf-sanity.yml
- docker-publish.yml
- verify-signature.yml
- release-sbom.yml

Each workflow focuses on a specific responsibility rather than combining
all steps into a single pipeline.

### Runtime Validation Workflows

The docker-smoke workflow ensures the container starts correctly.

The docker-smoke-readonly workflow verifies that the container
can run with a read-only filesystem.

These checks confirm that runtime restrictions do not break the service.

### Container Publishing

The docker-publish workflow builds the container image and pushes it
to GitHub Container Registry.

Publishing occurs only after the validation workflows succeed.

### Signature Verification

The verify-signature workflow confirms that the container image
signature matches the expected repository identity.

This ensures the published artifact was produced by the trusted CI pipeline.

### SBOM Generation

The release-sbom workflow generates a Software Bill of Materials
using Anchore Syft.

The SBOM is uploaded as a workflow artifact, making it accessible
for engineers who want to inspect the container dependencies.

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
