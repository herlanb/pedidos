from __future__ import annotations

from typing import Any
from uuid import UUID

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from domain import IdempotencyRecord, from_iso, to_iso


class DuplicateIdempotencyKeyError(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(f"idempotencia key ya usada: {key}")
        self.key = key


class IdempotencyRepository:
    def __init__(self, table: Any) -> None:
        self.table = table

    def reserve(self, record: IdempotencyRecord) -> None:
        try:
            self._table.put_item(
                Item={
                    "PK": record.pk,
                    "SK": record.sk,
                    "idempotency_key": record.idempotency_key,
                    "order_id": str(record.order_id),
                    "created_at": to_iso(record.created_at),
                },
                ConditionExpression=Attr("PK").not_exists(),
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise DuplicateIdempotencyKeyError(record.idempotency_key) from exc
            raise
    
    def get(self, idempotency_key: str) -> IdempotencyRecord | None:
        resp = self._table.get_item(
            Key={"PK": f"IDEMP#{idempotency_key}", "SK": IdempotencyRecord.SK_VALUE}
        )

        item = resp.get("Item")
        if not item:
            return None

        return IdempotencyRecord(
            idempotency_key=item["idempotency_key"],
            order_id=UUID(item["order_id"]),
            created_at=from_iso(item["created_at"]),
        )