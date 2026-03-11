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

The Secure Fraud Detection API demonstrates a verifiable container
supply-chain model.

The primary goal is to ensure that the container artifact published
in the registry can be independently verified by engineers.

The design focuses on three security guarantees:

- artifact authenticity
- build provenance
- dependency transparency

### Artifact Signing

Container images are signed using Cosign.

The signing process occurs during the CI pipeline after the container
image is successfully built and pushed to GitHub Container Registry.

Instead of storing signing keys inside the repository, the pipeline
uses keyless signing with GitHub OpenID Connect (OIDC).

This allows the signing process to bind the image to the repository
identity that produced it.

### Identity Verification

The Cosign verification process validates the certificate identity
embedded in the image signature.

The expected identity is the GitHub Actions workflow that produced
the artifact.

Engineers can confirm this identity using the verification command
shown in the project documentation.

This step ensures that the container image was produced by the
trusted CI workflow rather than an external source.

### Digest-Based Verification

Container images can also be verified using their SHA256 digest.

Digest verification guarantees that the pulled image matches the
exact artifact produced by the CI pipeline.

Combining signature verification with digest validation provides
strong guarantees about artifact authenticity.

### Independent Verification

One of the primary goals of the architecture is to enable independent
verification.

Any engineer can:

1. Pull the container image from GHCR
2. Verify the Cosign signature
3. Inspect the SBOM

This removes the need to trust the CI system blindly and allows
external validation of the artifact.

---

## VII. Dependency Transparency

The Secure Fraud Detection API exposes container dependencies through
Software Bill of Materials (SBOM) generation.

An SBOM provides a structured list of all packages and components
included in the container image.

This allows engineers to inspect the software composition of the
artifact and detect unexpected dependencies.

### SBOM Generation

The project uses Anchore Syft to generate the SBOM.

Syft scans the container image and extracts dependency information
from the filesystem layers.

The resulting SBOM is produced in SPDX JSON format.

### CI Integration

SBOM generation occurs during the CI pipeline after the container
image is built and signed.

The SBOM generation process is implemented in the following workflow:

release-sbom.yml

The workflow runs Syft against the container image published in
GitHub Container Registry.

### Artifact Publication

The generated SBOM is uploaded as a workflow artifact.

This makes the dependency report accessible through the GitHub
Actions run page.

Engineers reviewing the build can download the SBOM artifact
and inspect the container contents independently.

### Local Inspection

Engineers can also generate or inspect the SBOM locally.

Example command:

syft ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

This command produces a dependency report directly from the
published container image.

---

## VIII. Verification Workflow

How engineers independently verify the container artifact.

---

## IX. Design Tradeoffs

Why these tools were selected
What alternatives exist
