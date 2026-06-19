from dataclasses import dataclass


@dataclass
class Order:
    id: int | None
    user_id: int
    product_id: int
    quantity: int
    status: str = "new"
