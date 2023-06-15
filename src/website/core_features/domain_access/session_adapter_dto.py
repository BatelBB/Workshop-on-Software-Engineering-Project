from dataclasses import dataclass
from typing import Optional, Mapping


@dataclass
class ProductDto:
    name: str
    price: float
    category: str
    rate: Optional[float]
    quantity: int
    keywords: str
    store_name: str
    isBid: bool


@dataclass
class BasketDto:
    store_name: str
    amounts: Mapping[str, int]
    products: Mapping[str, ProductDto]