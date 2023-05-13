from abc import ABC, abstractmethod

from dev.src.main.Market.Appointment import Appointment
from dev.src.main.Market.Permissions import Permission
from dev.src.main.Store.Product import Product
from dev.src.main.Store.Store import Store
from dev.src.main.User.Cart import Cart
from dev.src.main.Utils.IConcurrentSingelton import IAbsractConcurrentSingleton
from dev.src.main.Utils.Response import Response
from dev.src.main.Utils.Session import Session


class IService(metaclass=IAbsractConcurrentSingleton):
    @abstractmethod
    def enter(self) -> Session:
        ...

    @abstractmethod
    def leave(self, identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def close_session(self, session_identifier: int) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...

    @abstractmethod
    def register(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_registered(self, username: str) -> bool:
        ...

    @abstractmethod
    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        ...

    @abstractmethod
    def is_logged_in(self, username: str) -> bool:
        ...

    @abstractmethod
    def logout(self, session_identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        ...

    # list[storeDTO]
    @abstractmethod
    def get_all_stores(self, session_identifier: int) -> Response[list[Store] | bool]:
        ...

    @abstractmethod
    def get_store(self, session_identifier: int, store_name: str) -> Response[Store | bool]:
        ...

    @abstractmethod
    def get_all_products_of(self, session_identifier: int, store_name: str) -> Response[set[Product] | bool]:
        ...

    @abstractmethod
    def get_product_by_name(self, session_identifier: int, product_name: str) -> Response[list[(str, Product)]]:
        ...

    @abstractmethod
    def get_product_by_category(self, session_identifier: int, category: str) -> Response[list[(str, Product)]]:
        ...

    @abstractmethod
    def get_product_by_keywords(self, session_identifier: int, keywords: list[str]) -> Response[list[(str, Product)]]:
        ...

    @abstractmethod
    def get_product_in_price_range(self, session_identifier: int, min: float, max: float) -> Response[list[(str, Product)]]:
        ...

    @abstractmethod
    def get_amount_of(self, session_identifier: int, product_name: str, store_name: str) -> Response[int]:
        ...

    @abstractmethod
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        ...

    @abstractmethod
    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_to_cart(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product_from_cart(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def show_cart(self, session_identifier: int) -> Response[Cart]:
        ...

    @abstractmethod
    def appoint_manager(self, session_identifier: int, store_name: str, appointee_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_owner(self, session_identifier: int, store_name: str, appointee_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def appointees_at(self, session_identifier: int, store_name: str) -> Response[list[str]]:
        ...

    @abstractmethod
    def add_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> Response[bool]:
        ...

    @abstractmethod
    def remove_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> Response[bool]:
        ...

    @abstractmethod
    def permissions_of(self, session_identifier: int, store: str, subject: str) -> Response[set[Permission] | bool]:
        ...

    @abstractmethod
    def remove_appointment(self, session_identifier: int, fired_appointee: str, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def reopen_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_staff(self, session_identifier: int, store_name: str) -> Response[list[Appointment] | bool]:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...
