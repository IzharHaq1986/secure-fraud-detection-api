# Container Supply Chain Architecture

The diagram below shows the container supply-chain pipeline implemented in this project.

```mermaid
flowchart LR
    A[Developer Commit] --> B[GitHub Actions CI]
    B --> C[Build Distroless Container]
    C --> D[Push Image to GHCR]
    D --> E[Cosign Sign Image]
    E --> F[Verify Signature]
    F --> G[Generate SBOM with Syft]
    G --> H[Publish SBOM Artifact]
    H --> I[Consumers Pull Image]
    I --> J[cosign verify command]
