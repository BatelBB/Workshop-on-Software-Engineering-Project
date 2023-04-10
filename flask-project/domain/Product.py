from interfaces import IProduct


class Product(IProduct):
    def __init__(self, ID: int, name: str, price: float):
        self.__ID = ID
        self.__name = name
        self.__price = price
