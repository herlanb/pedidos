from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from domain import Client


class CreateClientRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr

    def to_domain(self) -> Client:
        return Client(
            name=self.name,
            email=str(self.email)
        )


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    created_at: datetime

    @classmethod
    def from_domain(cls, client: Client) -> "ClientResponse":
        return cls(
            id=client.id,
            name=client.name,
            email=client.email,
            created_at=client.create_at
        )