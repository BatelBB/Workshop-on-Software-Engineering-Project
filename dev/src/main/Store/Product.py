from typing import Optional


class Product:
    def __init__(self, name: str, category: str = "whatever", price: float = 0.0, keywords: Optional[list[str]] = None):
        self.rate = None
        self.name = name
        self.category = category
        self.price = price
        if keywords is None:
            keywords = []
        self.keywords = keywords
        self.keywords.append(name)

    def __str__(self):
        rate: str = 'Not rated yet' if self.is_unrated() else self.rate
        return f'Product \'{self.name}\', Category: \'{self.category}\', Price: {self.price}, Rate: {rate}'

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def is_unrated(self):
        return self.rate is None
