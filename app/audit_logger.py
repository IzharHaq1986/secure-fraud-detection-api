"""
audit_logger.py

Audit logging in JSON Lines (JSONL) format with a tamper-evident hash chain.

Security intent:
- Each audit record includes:
    - prev_hash: hash of the previous record line
    - record_hash: hash of the current record (including prev_hash)
- If any line is edited/removed/reordered, downstream hashes will not validate.

Notes:
- This is not full "write-once" storage.
- It is a practical integrity signal suitable for a portfolio demo.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_LOG_DIR = Path("logs")
_AUDIT_LOG_PATH = _LOG_DIR / "audit.log"


def _utc_now_iso() -> str:
    """
    Return an ISO-8601 UTC timestamp with 'Z' suffix.
    Example: 2026-02-13T10:15:30.123456Z
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_text(text: str) -> str:
    """
    Compute SHA-256 hex digest of a text string.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_last_line(path: Path) -> str:
    """
    Read the last line of a text file efficiently.

    Returns:
        The last line as a string (without trailing newline), or "" if file doesn't exist/empty.
    """
    if not path.exists():
        return ""

    # Read file from the end in binary mode.
    with path.open("rb") as f:
        f.seek(0, 2)
        file_size = f.tell()

        if file_size == 0:
            return ""

        # Read backwards until we hit a newline.
        chunk_size = 1024
        data = b""
        offset = min(file_size, chunk_size)

        while offset > 0:
            f.seek(file_size - offset)
            data = f.read(offset) + data
            if b"\n" in data:
                break
            offset = min(file_size, offset + chunk_size)

    lines = data.splitlines()
    return lines[-1].decode("utf-8") if lines else ""


def _extract_record_hash(last_line: str) -> str:
    """
    Extract record_hash from the last JSONL line.

    If the last line is missing or malformed, we fall back to a known constant.
    """
    if not last_line.strip():
        return "0" * 64  # genesis hash

    try:
        obj = json.loads(last_line)
        record_hash = str(obj.get("record_hash", "")).strip()
        return record_hash if record_hash else "0" * 64
    except Exception:
        # If log is corrupted, fail closed to genesis.
        # In a stricter system, you'd raise and stop logging.
        return "0" * 64


def write_audit_event(event: Dict[str, Any]) -> None:
    """
    Append a single audit event to logs/audit.log with integrity chaining.

    Important:
    - Do NOT log raw PII or sensitive payloads.
    - Keep events minimal, intentional, and stable.
    """
    _LOG_DIR.mkdir(exist_ok=True)

    # Determine previous record hash.
    last_line = _read_last_line(_AUDIT_LOG_PATH)
    prev_hash = _extract_record_hash(last_line)

    # Create a new record object without mutating caller data.
    record = dict(event)
    record["timestamp"] = _utc_now_iso()
    record["prev_hash"] = prev_hash

    # Serialize without record_hash first.
    # This stable JSON string becomes the basis for the record_hash.
    record_without_hash = json.dumps(record, separators=(",", ":"), ensure_ascii=False)

    # Compute record hash using the serialized content.
    record_hash = _sha256_text(record_without_hash)
    record["record_hash"] = record_hash

    # Final JSONL line to append.
    line = json.dumps(record, separators=(",", ":"), ensure_ascii=False)

    with _AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
