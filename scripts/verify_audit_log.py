"""
verify_audit_log.py

Verifies the tamper-evident hash chain in logs/audit.log.

How it works:
- Each line is a JSON object containing:
    - prev_hash: record_hash of the previous line
    - record_hash: SHA-256 hash of the record content (excluding record_hash itself)

This script:
1) Reads the audit log line-by-line.
2) Recomputes the expected record_hash for each line.
3) Ensures:
   - computed_hash == stored record_hash
   - current prev_hash == previous stored record_hash

Exit codes:
- 0: verification success
- 1: verification failed (tampering or corruption detected)
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict


def sha256_text(text: str) -> str:
    """
    Return SHA-256 hex digest for a UTF-8 string.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_record_hash(record: Dict[str, Any]) -> str:
    """
    Compute a record hash exactly the same way the logger does:
    - Exclude 'record_hash'
    - Serialize with stable separators
    - Hash the resulting string
    """
    clone = dict(record)
    clone.pop("record_hash", None)

    serialized = json.dumps(clone, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(serialized)


def verify_audit_log(path: Path) -> bool:
    """
    Verify the full audit log hash chain.

    Returns:
        True if valid, False otherwise.
    """
    if not path.exists():
        print(f"ERROR: audit log not found: {path}")
        return False

    previous_record_hash = "0" * 64  # genesis hash

    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                # Empty lines are considered corruption.
                print(f"ERROR: empty line detected at line {idx}")
                return False

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"ERROR: invalid JSON at line {idx}: {exc}")
                return False

            prev_hash = str(obj.get("prev_hash", "")).strip()
            stored_hash = str(obj.get("record_hash", "")).strip()

            if not prev_hash or not stored_hash:
                print(f"ERROR: missing prev_hash/record_hash at line {idx}")
                return False

            # Validate chain linkage
            if prev_hash != previous_record_hash:
                print(
                    "ERROR: hash chain broken at line "
                    f"{idx}. expected prev_hash={previous_record_hash} "
                    f"but found prev_hash={prev_hash}"
                )
                return False

            # Validate record integrity
            computed_hash = compute_record_hash(obj)
            if computed_hash != stored_hash:
                print(
                    "ERROR: record hash mismatch at line "
                    f"{idx}. expected record_hash={computed_hash} "
                    f"but found record_hash={stored_hash}"
                )
                return False

            previous_record_hash = stored_hash

    print("OK: audit log hash chain verified successfully.")
    return True


def main() -> int:
    """
    CLI entry point.
    """
    log_path = Path("logs/audit.log")
    return 0 if verify_audit_log(log_path) else 1


if __name__ == "__main__":
    raise SystemExit(main())
