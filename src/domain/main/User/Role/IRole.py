from abc import ABC, abstractmethod

from domain.main.Store.Product import Product
from domain.main.Utils.Response import Response


class IRole(ABC):
    def __init__(self, context):
        self.context = context
        self.next: IRole

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
    def open_store(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_product(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_to_cart(self, store_name: str, product_name: str, price: float, quantity: int) -> Response[bool]:
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
    def empty_basket(self, store_name: str):
        ...

    @abstractmethod
    def is_allowed_to_appoint_owner(self, store_name: str, new_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_appoint_manager(self, store_name: str, new_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def make_me_owner(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def make_me_manager(self, store_name: str) -> Response[bool]:
        ...
    @abstractmethod
    def change_product_name(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, store_name: str, product_price: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_fire_employee(self, store_name:str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_get_store_purchase_history(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_shutdown_market(self) -> Response[bool]:
        ...

    @abstractmethod
    def set_stock_permissions(self, store_name: str, give_or_take: bool) -> Response[bool]:
        ...

    @abstractmethod
    def set_personal_permissions(self, store_name: str, give_or_take: bool) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_change_permissions(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_allowed_to_view_store_personal(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def purchase_shopping_cart(self, payment_method: str, payment_details: list) -> Response[bool]:
        ...