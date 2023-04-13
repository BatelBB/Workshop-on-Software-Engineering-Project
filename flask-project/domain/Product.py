from interfaces import IProduct


class Product(IProduct):
    def __init__(self, ID: int, name: str, price: float, category: str):
        self.ID = ID
        self.name = name
        self.price = price
        self.category = category

    def getPrice(self, ID: int):
        return self.price

    def getCategory(self, ID: int):
        return self.category



