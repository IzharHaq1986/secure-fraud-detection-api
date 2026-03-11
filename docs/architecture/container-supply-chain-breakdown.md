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

One of the primary design goals of this project is enabling engineers to
independently verify the container artifact produced by the CI pipeline.

The verification process can be performed using publicly available tools
and does not require access to the repository’s CI environment.

### Step 1 — Retrieve the Container Image

The container image can be pulled directly from GitHub Container Registry.

Example:

docker pull ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

This retrieves the published artifact produced by the CI pipeline.

### Step 2 — Verify the Image Signature

The container image is signed during the CI pipeline using Cosign with
GitHub OIDC identity.

Engineers can verify the signature using the following command:

cosign verify \
  --certificate-identity "https://github.com/IzharHaq1986/secure-fraud-detection-api/.github/workflows/docker-publish.yml@refs/tags/vX.Y.Z" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

This command confirms that the container image was produced by the
expected GitHub Actions workflow.

### Step 3 — Inspect the Software Bill of Materials

The SBOM can be inspected locally using Syft.

Example:

syft ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

This produces a dependency report that lists all packages included in
the container image.

### Independent Artifact Validation

These verification steps allow engineers to confirm:

- the container image was produced by the expected CI pipeline
- the artifact has not been modified
- the dependency composition of the container

This capability is an important property of verifiable software supply chains.

---

## IX. Design Tradeoffs

The Secure Fraud Detection API architecture prioritizes verifiability
and supply-chain transparency over operational complexity.

Several design decisions were made to balance simplicity with
security guarantees.

### Distroless Runtime

The container runtime uses a Distroless base image to reduce the
available attack surface.

This removes tools such as shells and package managers from the
runtime environment.

The tradeoff is that debugging inside the container becomes more
difficult compared to traditional images.

### Keyless Container Signing

The project uses Cosign keyless signing with GitHub OIDC identity.

This approach avoids managing private signing keys inside the
repository or CI pipeline.

However, it requires engineers to understand identity-based
verification rather than traditional key-based signing.

### SBOM as Workflow Artifact

The SBOM generated by the CI pipeline is stored as a workflow
artifact instead of a release asset.

This design choice avoids conflicts with immutable release
policies.

The tradeoff is that engineers must navigate to the CI workflow
run to retrieve the SBOM artifact.

### Multi-Workflow CI Design

The CI pipeline separates validation tasks across multiple
workflows rather than combining them into a single pipeline.

This makes failures easier to isolate and improves readability
of the automation.

The tradeoff is a slightly larger number of workflow files
in the repository.

### Simplicity of the Application Layer

The FastAPI application itself remains intentionally minimal.

The purpose of the repository is to demonstrate the container
supply-chain architecture rather than complex application
logic.

This makes the infrastructure design easier to understand,
but the service does not represent a full production system.

## X. Threat Model

The architecture of the Secure Fraud Detection API was designed
with several supply-chain security threats in mind.

The goal is not to eliminate all risk but to reduce the likelihood
of artifact compromise and improve transparency.

### Artifact Substitution

A malicious actor could replace a container image in the registry.

Mitigation:

Container images are signed using Cosign and verified using
GitHub OIDC identity. This allows engineers to confirm the
artifact was produced by the expected CI workflow.

### Dependency Injection

Unexpected dependencies could be introduced during the build
process or through compromised packages.

Mitigation:

SBOM generation provides visibility into the container contents.
Engineers can inspect dependencies using Syft.

### CI Pipeline Tampering

An attacker could attempt to modify the build pipeline to
produce unauthorized artifacts.

Mitigation:

GitHub branch protection and required status checks ensure
changes to the pipeline must pass CI verification.

### Runtime Privilege Escalation

Containers running with excessive privileges increase the
impact of potential vulnerabilities.

Mitigation:

The runtime container uses a Distroless base image and
runs as a non-root user with restricted filesystem access.
