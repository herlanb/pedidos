from __future__ import annotations

from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REVIEW = "REVIEW"
    FAILED = "FAILED"

_ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING: frozenset(
        {
            OrderStatus.COMPLETED,
            OrderStatus.REVIEW,
            OrderStatus.FAILED
        }
    ),
    OrderStatus.COMPLETED: frozenset(),
    OrderStatus.REVIEW: frozenset(),
    OrderStatus.FAILED: frozenset()
}

def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    """Indica si la transición es válida"""
    return target in _ALLOWED_TRANSITIONS[current]

def is_terminal(status: OrderStatus) -> bool:
    """Indica si el estado es terminal (sin transisiones salientes)"""
    return len(_ALLOWED_TRANSITIONS[status]) == 0