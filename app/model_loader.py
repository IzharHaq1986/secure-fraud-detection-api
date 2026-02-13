import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ModelHandle:
    """
    Lightweight model handle for v1.

    For now, we don't load a real ML model yet.
    We validate the artifact integrity and return metadata.
    """
    version: str
    artifact_path: str


_MANIFEST_PATH = Path("model_artifacts/manifest.json")


def _sha256_file(path: Path) -> str:
    """
    Compute SHA-256 of a file in a streaming manner.
    This avoids loading the whole file into memory.
    """
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)  # 1 MB
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()


def load_active_model() -> ModelHandle:
    """
    Load the active model definition from the manifest and validate integrity.

    Security intent:
    - Prevent silent model replacement
    - Ensure deployed artifact matches the approved checksum
    """
    if not _MANIFEST_PATH.exists():
        raise RuntimeError("Model manifest not found: model_artifacts/manifest.json")

    manifest: Dict[str, Any] = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    active = manifest.get("active_model")

    if not active:
        raise RuntimeError("Manifest missing 'active_model' section.")

    version = str(active.get("version", "")).strip()
    artifact_path_str = str(active.get("path", "")).strip()
    expected_sha256 = str(active.get("sha256", "")).strip().lower()

    if not version or not artifact_path_str or not expected_sha256:
        raise RuntimeError("Manifest active_model must include version, path, sha256.")

    artifact_path = Path(artifact_path_str)

    if not artifact_path.exists():
        raise RuntimeError(f"Model artifact not found: {artifact_path_str}")

    actual_sha256 = _sha256_file(artifact_path)

    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            "Model artifact checksum mismatch. "
            f"expected={expected_sha256} actual={actual_sha256}"
        )

    return ModelHandle(version=version, artifact_path=str(artifact_path))
