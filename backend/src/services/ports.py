from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

class WorkflowTrigger(Protocol):
    def start(self, order_id: UUID, order_input: dict[str, Any]) -> str | None:
        ...