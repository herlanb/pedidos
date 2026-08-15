from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .time import utcnow
from .order_status import OrderStatus, can_transition


class InvalidOrderError(ValueError):
    """Error de dominio: los datos de la orden no cumplen los requisitos"""


class InvalidTransitionError(RuntimeError):
    """Error de dominio: intento de transición de estado no permitido"""


RISK_REVIEW_THRESHOLD = 70


@dataclass
class Order:
    client_id: UUID
    amount: float
    currency: str
    item_count: int
    is_international: bool
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.PENDING
    risk_score: int | None = None
    create_at: datetime = field(default_factory=utcnow)
    update_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.amount <= 0:
            raise InvalidOrderError("amount debe ser mayor que 0")

        if not self.currency or len(self.currency) != 3:
            raise InvalidOrderError("currency debe ser un código ISO de 3 letras")

        if self.item_count <= 0:
            raise InvalidOrderError("item_count debe ser mayor que 0")

        if self.risk_score is not None and not 0 <= self.risk_score <= 100:
            raise InvalidOrderError("risk_score debe estar entre 0 y 100")

    def assign_risk_score(self, score: int) -> None:
        """Registra el risk_score calculado por el workflow"""

        if not 0 <= score <= 100:
            raise InvalidOrderError("risk_score debe estar entre 0 y 100")

        self.risk_score = score
        self.update_at = utcnow()

    def transition_to(self, target: OrderStatus) -> None:
        """Cambia el estado validando que la transición sea legal""" 

        if not can_transition(self.status, target):
            raise InvalidTransitionError(
                f"transición inválida: {self.status} -> {target.value}"
            )

        self.status = target
        self.update_at = utcnow()

    def resolve_by_risk(self) -> OrderStatus:
        """Estado destino según risk_score"""

        if self.risk_score is None:
            raise InvalidOrderError("no se puede resolver sin risk_score")

        return (
            OrderStatus.REVIEW
            if self.risk_score >= RISK_REVIEW_THRESHOLD 
            else OrderStatus.COMPLETED
        )