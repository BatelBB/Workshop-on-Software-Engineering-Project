from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductDto:
    name: str
    price: float
    category: str
    rate: Optional[float]
    quantity: int
