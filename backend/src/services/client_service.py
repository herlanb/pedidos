from __future__ import annotations

import logging
from collections.abc import Callable
from uuid import UUID

from domain import Client
from api.schemas import CreateClientRequest

from .exceptions import ClientNotFoundError
from .unit_of_work import PostgresUnitOfWork

logger = logging.getLogger(__name__)

class ClientService:
    def __init__(self, uow_factory: Callable[[], PostgresUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def create_client(self, request: CreateClientRequest) -> Client:
        client = request.to_domain()
        with self._uow_factory() as uow:
            uow.clients.add(client)
            uow.commit()

        logger.info("Cliente creado", extra={"client_id": str(client.id)})
        return client

    def get_client(self, client_id: UUID) -> Client:
        with self._uow_factory() as uow:
            client = uow.clients.get(client_id)
        if client is None:    
            raise ClientNotFoundError(str(client_id))

        return client