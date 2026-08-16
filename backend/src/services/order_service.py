from __future__ import annotations

import logging
from collections.abc import Callable
from uuid import UUID

from domain import EventType, ExecutionEvent, IdempotencyRecord, Order
from api.schemas import CreateOrderRequest
from repositories.dynamo import (
    DuplicateIdempotencyKeyError,
    EventRepository,
    IdempotencyRepository
)

from .exceptions import ClientNotFoundError, OrderNotFoundError
from .ports import WorkflowTrigger
from .unit_of_work import PostgresUnitOfWork

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        uow_factory: Callable[[], PostgresUnitOfWork],
        event_repo: EventRepository,
        idempotency_repo: IdempotencyRepository,
        workflow: WorkflowTrigger
    ) -> None:
        self._uow_factory = uow_factory
        self._events = event_repo
        self._idempotency = idempotency_repo
        self._workflow = workflow

    def create_order(
        self,
        request: CreateOrderRequest,
        idempotency_key: str
    ) -> tuple[Order, bool]:
        order = request.to_domain()

        with self._uow_factory() as uow:
            if uow.clients.get(order.client_id) is None:
                raise ClientNotFoundError(str(order.client_id))

        try:
            self._idempotency.reserve(
                IdempotencyRecord(
                    idempotency_key=idempotency_key, 
                    order_id=order.id
                )
            )

        except DuplicateIdempotencyKeyError:
            existing = self._idempotency.get(idempotency_key)
            assert existing is not None
            logger.info(
                "Error, idempotency key falla porque ya existe",
                extra={
                    "idempotency_key": idempotency_key, 
                    "order_id": str(existing.order_id)
                }
            )

            return self._require_order(existing.order_id), False

        # Intentamos guardar la orden en Postgres
        try:
            with self._uow_factory() as uow:
                uow.orders.add(order)
                uow.commit()

        except Exception:
            self._idempotency.release(idempotency_key)
            logger.exception(
                "Error al guardar la orden, liberamos idempotency key",
                extra={
                    "idempotency_key": idempotency_key,
                    "order_id": str(order.id)
                }
            )

            raise

        self._events.append(
            ExecutionEvent(
                order_id=order.id,
                event_type=EventType.ORDER_CREATED,
                payload={
                    "amount": order.amount,
                    "currency": order.currency,
                    "item_count": order.item_count,
                    "is_international": order.is_international,
                    "status": order.status
                }
            )
        ) 

        logger.info("Orden creada", extra={"order_id": str(order.id)})   

        # Disparmos el worflow
        try:
            self._workflow.start(
                order.id,
                {
                    "order_id": str(order.id),
                    "client_id": str(order.client_id),
                    "amount": order.amount,
                    "currency": order.currency,
                    "item_count": order.item_count,
                    "is_international": order.is_international
                }
            )

        except Exception:
            logger.exception(
                "Error con el Workflow. La orden queda en estado PENDING",
                extra={"order_id": str(order.id)}
            )

        return Order, True

    def get_order(self, order_id: UUID) -> Order:
        return self._require_order(order_id)

    def get_order_events(self, order_id: UUID) -> list[ExecutionEvent]:
        self._require_order(order_id)

        return self._events.list_for_order(order_id)

    def _require_order(self, order_id: UUID) -> Order:
        with self._uow_factory() as uow:
            order = uow.orders.get(order_id)

        if order is None:
            raise OrderNotFoundError(str(order_id))

        return order