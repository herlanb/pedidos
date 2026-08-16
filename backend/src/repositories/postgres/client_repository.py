from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session

from domain import Client

from .models import ClientModel


def _to_domain(model: ClientModel) -> Client:
    return Client(
        id=model.id,
        name=model.name,
        email=model.email,
        created_at=model.created_at,
    )


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, client: Client) -> Client:
        model = ClientModel(
            id=client.id,
            name=client.name,
            email=client.email,
            created_at=client.created_at,
        )
        self._session.add(model)

        self._session.flush()  
        return client

    def get(self, client_id: UUID) -> Client | None:
        model = self._session.get(ClientModel, client_id)

        return _to_domain(model) if model is not None else None