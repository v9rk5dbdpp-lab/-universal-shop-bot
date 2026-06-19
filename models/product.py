from dataclasses import dataclass


@dataclass
class Product:
    id: int | None
    name: str
    description: str
    price: int
    photo_file_id: str | None = None
    is_active: bool = True
    stock: int = 0
