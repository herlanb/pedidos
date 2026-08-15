from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session

from domain import Order, OrderStatus

from .models import OrderModel


class OrderNotFoundError(Exception):
    """La orden no existe en la base."""


def _to_domain(model: OrderModel) -> Order:
    return Order(
        id=model.id,
        client_id=model.client_id,
        amount=model.amount,
        currency=model.currency,
        item_count=model.item_count,
        is_international=model.is_international,
        status=OrderStatus(model.status),
        risk_score=model.risk_score,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            client_id=order.client_id,
            amount=order.amount,
            currency=order.currency,
            item_count=order.item_count,
            is_international=order.is_international,
            status=order.status.value,
            risk_score=order.risk_score,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        self._session.add(model)
        self._session.flush()
        return order

    def get(self, order_id: UUID) -> Order | None:
        model = self._session.get(OrderModel, order_id)
        return _to_domain(model) if model is not None else None

    def update(self, order: Order) -> Order:
        """Persiste status, risk_score y updated_at de una orden existente."""

        model = self._session.get(OrderModel, order.id)
        if model is None:
            raise OrderNotFoundError(str(order.id))

        model.status = order.status.value
        model.risk_score = order.risk_score
        model.updated_at = order.updated_at

        self._session.flush()

        return order