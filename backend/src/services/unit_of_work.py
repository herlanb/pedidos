from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from sqlalchemy.orm import Session

from repositories.postgres import ClientRepository, OrderRepository

class PostgresUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> "PostgresUnitOfWork":
        self._session = self._session_factory()
        self.clients = ClientRepository(self._session)
        self.orders = OrderRepository(self._session)
        return self

    def __exit__(
        self, 
        exc_type: type[BaseException] | None,
        exc: BaseException | None, 
        tb: TracebackType | None
    ) -> None:
        if exc_type is not None:
            self._session.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
        