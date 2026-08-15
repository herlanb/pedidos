from __future__ import annotations
 
import json
from typing import Any
from uuid import UUID
 
from boto3.dynamodb.conditions import Key
 
from domain import EventType, ExecutionEvent, from_iso, to_iso

def _to_domain(item: dict[str, Any]) -> ExecutionEvent:
    return ExecutionEvent(
        order_id=UUID(item["order_id"]),
        event_type=EventType(item["event_type"]),
        timestamp=from_iso(item["timestamp"]),
        payload=json.loads(item.get("payload", "{}")),
    )

class EventRepository:
    def __init__(self, table: Any) -> None:
        self._table = table
 
    def append(self, event: ExecutionEvent) -> None:
        self._table.put_item(
            Item={
                "PK": event.pk,
                "SK": event.sk,
                "order_id": str(event.order_id),
                "event_type": event.event_type.value,
                "timestamp": to_iso(event.timestamp),
                "payload": json.dumps(event.payload, default=str),
            }
        )
 
    def list_for_order(self, order_id: UUID) -> list[ExecutionEvent]:
        events: list[ExecutionEvent] = []
        last_key: dict[str, Any] | None = None
        
        while True:
            kwargs: dict[str, Any] = {
                "KeyConditionExpression": Key("PK").eq(f"ORDER#{order_id}")
                & Key("SK").begins_with("EVENT#"),
                "ScanIndexForward": True, 
            }
            if last_key:
                kwargs["ExclusiveStartKey"] = last_key
            resp = self._table.query(**kwargs)
            events.extend(_to_domain(i) for i in resp.get("Items", []))
            last_key = resp.get("LastEvaluatedKey")
            if not last_key:
                break

        return events