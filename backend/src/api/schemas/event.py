from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from domain import EventType, ExecutionEvent


class ExecutionEventResponse(BaseModel):
    order_id: UUID
    event_type: EventType
    timestamp: datetime
    payload: dict[str, Any]

    @classmethod
    def from_domain(cls, event: ExecutionEvent) -> "ExecutionEventResponse":
        return cls(
            order_id=event.order_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload=event.payload
        )