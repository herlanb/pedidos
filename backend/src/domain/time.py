from __future__ import annotations

from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def to_iso(dt: datetime) -> str:
    """Serializa un datetime a string ISO 8601 en UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc).isoformat()

def from_iso(value: str) -> datetime:
    """Parsea un string ISO 8601 a datetime aware en UTC."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)