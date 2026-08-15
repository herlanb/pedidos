from __future__ import annotations

import os
from typing import Any

import boto3


def get_dynamo_resource() -> Any:
    endpoint = os.getenv("DYNAMODB_ENDPOINT_URL")  # http://localhost:8000
    region = os.getenv("AWS_REGION", "us-east-1")
    kwargs: dict[str, Any] = {"region_name": region}
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    return boto3.resource("dynamodb", **kwargs)


def get_table(resource: Any | None = None) -> Any:
    resource = resource or get_dynamo_resource()
    table_name = os.getenv("DYNAMODB_TABLE", "pedidos")
    return resource.Table(table_name)