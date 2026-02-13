import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Audit logs are written as JSON Lines (one JSON object per line).
# This format is:
# - easy to append
# - easy to ship to SIEM / log pipelines later
# - easy to parse for audits and incident review

_LOG_DIR = Path("logs")
_AUDIT_LOG_PATH = _LOG_DIR / "audit.log"


def _utc_now_iso() -> str:
    """
    Return an ISO-8601 UTC timestamp with a 'Z' suffix.
    Example: 2026-02-13T10:15:30.123456Z
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_audit_event(event: Dict[str, Any]) -> None:
    """
    Append a single audit event to logs/audit.log in JSONL format.

    Important:
    - Do NOT log raw PII or sensitive payloads here.
    - Keep events minimal and intentional.
    """
    _LOG_DIR.mkdir(exist_ok=True)

    # Create a shallow copy so callers don't get their dict mutated.
    event_to_write = dict(event)
    event_to_write["timestamp"] = _utc_now_iso()

    # Ensure stable, compact JSON to make logs consistent.
    line = json.dumps(event_to_write, separators=(",", ":"), ensure_ascii=False)

    with _AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
