from __future__ import annotations

class ClientNotFoundError(Exception):
    def __init__(self, client_id: str) -> None:
        super().__init__(f"Cliente no encontrado: {client_id}")
        self.client_id = client_id

class OrderNotFoundError(Exception):
    def __init__(self, order_id) -> None:
        super().__init__(f"Orden no encontrada: {order_id}")
        self.order_id = order_id