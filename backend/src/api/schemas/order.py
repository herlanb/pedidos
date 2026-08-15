from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain import Order, OrderStatus

class CreateOrderRequest(BaseModel):
    client_id: UUID
    amount: float = Field(gt=0, description="Monto de la orden mayor que 0")
    currency: str = Field(min_length=3, max_length=3, description="Código ISO 4217")
    item_count: int = Field(gt=0)
    is_international: bool = False

    @field_validator("currency")
    @classmethod
    def _normalize_currency(cls, value: str) -> str:
        return value.upper()

    def to_domain(self) -> Order:
        return Order(
            client_id=self.client_id,
            amount=self.amount,
            currency=self.currency,
            item_count=self.item_count,
            is_international=self.is_international
        )

class OrderResponse(BaseModel):
    """Representa salida de una orden"""
    
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    amount: float
    currency: str
    item_count: int
    is_international: bool
    status: OrderStatus
    risk_score: int | None
    created_at: datetime
    update_at: datetime

    @classmethod
    def from_domain(cls, order: Order) -> "OrderResponse":
        return cls(
            id=order.id,
            client_id=order.client_id,
            amount=order.amount,
            currency=order.currency,
            item_count=order.item_count,
            is_international=order.is_international,
            status=order.status,
            risk_score=order.risk_score,
            created_at=order.created_at,
            updated_at=order.updated_at
        )