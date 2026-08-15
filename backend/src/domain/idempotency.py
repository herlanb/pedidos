from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .time import utcnow

@dataclass
class IdempotencyRecord:
    idempotency_key: str
    order_id: UUID
    create_at: datetime = field(default_factory=utcnow)

    SK_VALUE = "META"

    def __post_init__(self) -> None:
        if not self.idempotency_key or not self.idempotency_key.strip():
            raise ValueError("idempotency_key no puede estar vacío")

    @property
    def pk(self) -> str:
        return f"IDEMP#{self.idempotency_key}"

    @property
    def sk(self) -> str:
        return self.SK_VALUE