from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from .time import to_iso, utcnow


class EventType(str, Enum):
    """Tipos de eventos que registra el workflow"""

    ORDER_CREATED = "ORDER_CREATED"
    VALIDATED = "VALIDATED"
    RISK_CALCULATED = "RISK_CALCULATED"
    COMPLETED = "COMPLETED"
    REVIEW = "REVIEW"
    FAILED = "FAILED"


@dataclass
class ExecutionEvent:
    """Evento de ejecución asociado a una orden"""

    order_id: UUID
    event_type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utcnow)

    @property
    def pk(self) -> str:
        return f"ORDER#{self.order_id}"

    @property
    def sk(self) -> str:
        return f"EVENT#{to_iso(self.timestamp)}#{self.event_type.value}"    