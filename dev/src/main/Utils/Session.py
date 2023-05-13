from typing import Any

from dev.src.main.Market.Appointment import Appointment
from dev.src.main.Market.Permissions import Permission
from dev.src.main.Service import IService
from dev.src.main.Store.Product import Product
from dev.src.main.Store.Store import Store
from dev.src.main.User.Cart import Cart
from dev.src.main.Utils.Logger import report, Logger
from dev.src.main.Utils.Response import Response


# At most one member can be logged-in in a session.
class Session:
    def __init__(self, identifier: int, service: IService):
        self.identifier = identifier
        self.service = service
        self.is_open = True

    def __str__(self):
        return f'Session: {self.identifier}'

    def report_session_closed(self) -> Response[bool]:
        return report(f'Attempted to use a closed {self})', False, Logger.Severity.ERROR)

    def leave(self):
        self.is_open = False
        return self.service.leave(self.identifier)

    def register(self, username: str, encrypted_password: str) -> Response[bool]:
        if self.is_open:
            return self.service.register(self.identifier, username, encrypted_password)
        else:
            return self.report_session_closed()

    def is_registered(self, username: str) -> bool:
        return self.is_open and self.service.is_registered(username)

    def login(self, username: str, encrypted_password: str) -> Response[bool]:
        if self.is_open:
            return self.service.login(self.identifier, username, encrypted_password)
        else:
            return self.report_session_closed()

    def is_logged_in(self, username: str) -> bool:
        return self.is_open and self.service.is_logged_in(username)

    def logout(self) -> Response[bool]:
        if self.is_open:
            return self.service.logout(self.identifier)
        else:
            return self.report_session_closed()

    def open_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.open_store(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def get_all_stores(self) -> Response[list[Store] | bool]:
        if self.is_open:
            return self.service.get_all_stores(self.identifier)
        else:
            return self.report_session_closed()

    def get_store(self, store_name: str) -> Response[Store | bool]:
        if self.is_open:
            return self.service.get_store(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def get_all_products_of(self, store_name: str) -> Response[set[Product] | bool]:
        if self.is_open:
            return self.service.get_all_products_of(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def get_product_by_name(self, product_name: str) -> Response[list[(str, Product)] | bool]:
        if self.is_open:
            return self.service.get_product_by_name(self.identifier, product_name)
        else:
            return self.report_session_closed()

    def get_product_by_category(self, category: str) -> Response[list[(str, Product)] | bool]:
        if self.is_open:
            return self.service.get_product_by_category(self.identifier, category)
        else:
            return self.report_session_closed()

    def get_product_by_keywords(self, keywords: list[str]) -> Response[list[(str, Product)] | bool]:
        if self.is_open:
            return self.service.get_product_by_keywords(self.identifier, keywords)
        else:
            return self.report_session_closed()

    def get_product_in_price_range(self, min: float, max: float) -> Response[list[(str, Product)] | bool]:
        if self.is_open:
            return self.service.get_product_in_price_range(self.identifier, min, max)
        else:
            return self.report_session_closed()

    def add_product(self, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str] = None) -> Response[bool]:
        if keywords is None:
            keywords = []
        if self.is_open:
            return self.service.add_product(self.identifier, store_name, product_name, category, price, quantity,
                                            keywords)
        else:
            return self.report_session_closed()

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) ->Response[bool]:
        if self.is_open:
            return self.service.update_product_quantity(self.identifier, store_name, product_name, quantity)
        else:
            return self.report_session_closed()

    def get_amount_of(self, product_name: str, store_name: str) -> Response[int]:
        if self.is_open:
            return self.service.get_amount_of(self.identifier, product_name, store_name)
        else:
            return self.report_session_closed()

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.remove_product(self.identifier, store_name, product_name)
        else:
            return self.report_session_closed()

    def add_to_cart(self, store_name: str, product_name: str, quantity: int = 1) -> Response[bool]:
        if self.is_open:
            return self.service.add_to_cart(self.identifier, store_name, product_name, quantity)
        else:
            return self.report_session_closed()

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.remove_product_from_cart(self.identifier, store_name, product_name)
        else:
            return self.report_session_closed()

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        if self.is_open:
            return self.service.update_cart_product_quantity(self.identifier, store_name, product_name, quantity)
        else:
            return self.report_session_closed()

    def show_cart(self) -> Response[Cart | bool]:
        if self.is_open:
            return self.service.show_cart(self.identifier)
        else:
            return self.report_session_closed()

    def appoint_manager(self, store: str, appointee: str) -> Response[bool]:
        if self.is_open:
            return self.service.appoint_manager(self.identifier, store, appointee)
        else:
            return self.report_session_closed()

    def appoint_owner(self, store: str, appointee: str) -> Response[bool]:
        if self.is_open:
            return self.service.appoint_owner(self.identifier, store, appointee)
        else:
            return self.report_session_closed()

    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        if self.is_open:
            return self.service.appointees_at(self.identifier, store)
        else:
            return self.report_session_closed()

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.remove_appointment(self.identifier, fired_appointee, store_name)
        else:
            return self.report_session_closed()

    def add_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        if self.is_open:
            return self.service.add_permission(self.identifier, store, appointee, permission)
        else:
            return self.report_session_closed()

    def remove_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        if self.is_open:
            return self.service.remove_permission(self.identifier, store, appointee, permission)
        else:
            return self.report_session_closed()

    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        if self.is_open:
            return self.service.permissions_of(self.identifier, store, subject)
        else:
            return self.report_session_closed()

    def close_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.close_store(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def reopen_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.reopen_store(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def get_store_staff(self, store_name: str) -> Response[list[Appointment] | bool]:
        if self.is_open:
            return self.service.get_store_staff(self.identifier, store_name)
        else:
            return self.report_session_closed()
