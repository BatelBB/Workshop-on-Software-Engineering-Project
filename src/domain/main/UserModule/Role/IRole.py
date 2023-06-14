from abc import ABC, abstractmethod

from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.Store import Store
from src.domain.main.Utils.Response import Response


class IRole(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def login(self, encrypted_password: str) -> bool:
        ...

    @abstractmethod
    def logout(self) -> Response[bool]:
        ...

    @abstractmethod
    def is_logged_in(self) -> bool:
        ...

    @abstractmethod
    def is_member(self) -> bool:
        ...

    @abstractmethod
    def add_to_cart(self, store_name: str, product_name: str, price: float, quantity: int = 1) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def show_cart(self) -> Response[dict]:
        ...

    @abstractmethod
    def verify_cart_not_empty(self) -> Response[bool]:
        ...

    @abstractmethod
    def get_baskets(self) -> dict:
        ...

    @abstractmethod
    def empty_basket(self, store_name: str) -> None:
        ...
