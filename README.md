![CI](https://github.com/IzharHaq1986/secure-fraud-detection-api/actions/workflows/ci.yml/badge.svg)

<!-- Tech Stack Badges -->
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green)
![Pydantic](https://img.shields.io/badge/Pydantic-2.x-ff69b4)
![Ruff](https://img.shields.io/badge/Linter-Ruff-000000)
![pytest](https://img.shields.io/badge/Tests-pytest-blueviolet)
![Coverage](https://img.shields.io/badge/Coverage-85%25+-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Ubuntu_24.02-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

# Secure Fraud Detection API
```
FastAPI-based fraud detection service packaged as a signed and verifiable container image.

Python 3.11 · FastAPI · Docker (Distroless) · GHCR · Cosign (OIDC) · SPDX SBOM · MIT License.
```
## Proof of Supply-Chain Security (Verify in 5 minutes)

This repository publishes a signed container image with verifiable provenance.

The build pipeline uses GitHub Actions with OIDC-based keyless signing and
generates a Software Bill of Materials (SBOM) during the release process.

Engineers can independently verify the container supply chain.

### Pull the Published Container Image

docker pull ghcr.io/izharhaq1986/secure-fraud-detection-api:v1.0.31

### Verify the Container Signature

cosign verify \
  --certificate-identity "https://github.com/IzharHaq1986/secure-fraud-detection-api/.github/workflows/docker-publish.yml@refs/tags/v1.0.31" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/izharhaq1986/secure-fraud-detection-api:v1.0.31

### Review the Software Bill of Materials

An SPDX JSON SBOM is generated during the release workflow using **Syft**.

Location:

GitHub → Actions → `release-sbom.yml` workflow → Artifacts → `sbom.spdx.json`

### Why This Matters

Modern software supply chains face risks such as dependency tampering,
artifact substitution, and compromised build environments.

This repository demonstrates production-grade practices:

• Keyless container signing using GitHub OIDC  
• Verifiable container provenance  
• Immutable container releases  
• SBOM generation for dependency transparency
```
## What This Repository Demonstrates
```
Secure API design for model inference
Audit-ready decision logging with trace IDs and model versioning
Threat modeling and risk-driven mitigation
Hardened container deployment with TLS-ready defaults
Signed container images with digest-based verification
Immutable releases with attached SBOM
This is structured as a client-facing sample. It is not a tutorial repo.
```
## Architecture Breakdown
```
A detailed architecture explanation of the container supply-chain pipeline
is available in the following document:

docs/architecture/container-supply-chain-breakdown.md

The breakdown explains:

- system context and design goals
- application architecture
- container runtime design
- CI/CD pipeline structure
- supply-chain security model
- artifact verification workflow
- engineering tradeoffs
```

## Architecture Diagram
```
The following diagram shows the container supply-chain pipeline implemented in this project.

See: `docs/diagrams/container-supply-chain-architecture.md`
```
## I. Project Structure
```
secure-fraud-detection-api/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app factory + router registration
│   ├── auth.py                # API-key authentication dependency
│   ├── schemas.py             # Pydantic request/response models
│   ├── middleware.py          # Security / rate limiting / request-id
│   ├── audit_logger.py        # Tamper-evident audit logging
│   ├── model_loader.py        # Model artifact loading & validation
│   └── routes/
│       └── predict.py         # /v1/predict endpoint
│
├── tests/
│   ├── conftest.py
│   ├── test_predict.py
│   └── test_routes_unique.py
│
├── scripts/
│   └── check_requirements_lock.sh
│
├── .github/
│   ├── workflows/
│   │   ├── docker-smoke.yml
│   │   ├── docker-smoke-readonly.yml
│   │   ├── docker-perf-sanity.yml
│   │   ├── docker-publish.yml
│   │   ├── verify-signature.yml
│   │   └── release-sbom.yml
│   └── dependabot.yml
│
├── requirements.txt
├── requirements.lock.txt
├── Dockerfile
└── README.md
```

## II. Getting Started
```
Run Locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Open:
http://localhost:8000/health
Expected:
{"status":"ok"}
Run with Docker
docker build -t fraud-api:local .
docker run -p 8000:8000 fraud-api:local
```

## III. Container Image (GHCR)
```
Pull a tagged release:
docker pull ghcr.io/izharhaq1986/secure-fraud-detection-api:v1.0.X
Pull by digest for immutability:
docker pull ghcr.io/izharhaq1986/secure-fraud-detection-api@sha256:<digest>
```

## IV. Release Process (Tags + SBOM)
```
This repository uses semantic version tags.
Each Git tag:
Publishes a container image to GHCR
Signs the image using Cosign (OIDC)
Verifies the signature in CI
Generates an SPDX JSON SBOM
Attaches the SBOM to the GitHub Release
Immutable release behavior is handled safely.
If asset uploads are rejected due to immutability, CI skips without failing.
```
## V. Supply Chain Verification
```
Resolve image digest:
crane digest ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z
Verify signature:
cosign verify \
  --certificate-identity "https://github.com/IzharHaq1986/secure-fraud-detection-api/.github/workflows/docker-publish.yml@refs/tags/vX.Y.Z" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/izharhaq1986/secure-fraud-detection-api@sha256:<digest>

Inspect SBOM:
syft ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z
```
## Quick Verification Example
```
The following commands demonstrate how an engineer can verify the
container artifact produced by this repository.

Pull the container image:

docker pull ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

Verify the container signature:

cosign verify \
  --certificate-identity "https://github.com/IzharHaq1986/secure-fraud-detection-api/.github/workflows/docker-publish.yml@refs/tags/vX.Y.Z" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

Inspect the Software Bill of Materials:

syft ghcr.io/izharhaq1986/secure-fraud-detection-api:vX.Y.Z

## VI. Screenshots

The following screenshots demonstrate the secure container supply-chain workflow implemented in this project.

### Docker Smoke Test

Container starts successfully and exposes the `/health` endpoint.

![Docker Smoke Test](docs/screenshots/docker-smoke_V1.0.png)

### Read-Only Container Execution

The container runs with a read-only filesystem, demonstrating runtime hardening.

![Read-Only Container](docs/screenshots/readonly-container_V1.0.png)

### GHCR Publish Workflow

Container image successfully published to GitHub Container Registry.

![GHCR Publish](docs/screenshots/ghcr-publish_V1.0.png)

### Cosign Signature Verification

Image signature verified using Cosign and GitHub OIDC identity.

![Cosign Verification](docs/screenshots/cosign-verify_V1.0.png)

### SBOM Generation

Software Bill of Materials generated using **Syft** and stored as a CI workflow artifact.

![SBOM Artifact](docs/screenshots/sbom-artifact_V1.0.png)

---

## VII. CI Enforcement

Required workflows:

- docker-smoke
- docker-smoke-readonly
- docker-perf-sanity
- docker-publish
- verify-signature
- release-sbom

Branch protection enforces required status checks.

---
## Documentation
```
The repository includes several documents explaining the system
architecture and container supply-chain design.

Architecture Index 
docs/architecture/index.md

Architecture Breakdown 
docs/architecture/container-supply-chain-breakdown.md

Architecture Diagram 
docs/diagrams/container-supply-chain-architecture.md

Technical Teardown Article 
docs/articles/teardown-verifiable-container-supply-chain.md

```
## VIII. Skills Demonstrated

- Secure FastAPI architecture
- Hardened Docker builds (Distroless, non-root)
- Digest-based signing
- Cosign keyless OIDC flow
- SBOM generation (SPDX)
- Immutable release handling
- Deterministic CI pipelines
- OCI naming compliance

---

## IX. License

MIT License.

See the `LICENSE` file for details.

Project Status:

- Build pipeline: stable
- Release flow: verified
- Signing: enforced
- SBOM: generated
- OCI compliance: validated
