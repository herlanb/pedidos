from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .time import utcnow


class InvalidClientError(ValueError):
    """Error de dominio: los datos del cliente no cumplen los requisitos"""


@dataclass
class Client:
    name: str
    email: str
    id: UUID = field(default_factory=uuid4)
    create_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidClientError("Name no puede estar vacío")

        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise InvalidClientError(f"Email inválido: {self.email!r}")