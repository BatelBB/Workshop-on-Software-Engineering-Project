from abc import ABC, abstractmethod

from dev.src.main.Store.Product import Product
from dev.src.main.Store.Store import Store
from dev.src.main.Utils.Response import Response


class IRole(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def leave(self, session_identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def register(self) -> Response[bool]:
        ...

    @abstractmethod
    def login(self, encrypted_password: str) -> Response[bool]:
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
    def is_admin(self) -> bool:
        ...

    @abstractmethod
    def add_to_cart(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def show_cart(self) -> str:
        ...
