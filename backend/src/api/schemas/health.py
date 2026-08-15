from __future__ import annotations
 
from typing import Literal
from pydantic import BaseModel
 
 
class DependencyStatus(BaseModel):
    postgres: bool
    dynamodb: bool
 
 
class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    dependencies: DependencyStatus
 
    @classmethod
    def from_checks(cls, postgres_ok: bool, dynamo_ok: bool) -> "HealthResponse":
        return cls(
            status="ok" if (postgres_ok and dynamo_ok) else "degraded",
            dependencies=DependencyStatus(
                postgres=postgres_ok, 
                dynamodb=dynamo_ok
            )
        )