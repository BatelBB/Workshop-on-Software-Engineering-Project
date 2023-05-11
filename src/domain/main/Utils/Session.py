from typing import Any

from src.domain.main.Service import IService
from src.domain.main.Utils.Logger import report, Logger
from src.domain.main.Utils.Response import Response


# At most one member can be logged-in in a session.
class Session:
    def __init__(self, identifier: int, service):
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

    def close_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.close_store(self.identifier, store_name)
        else:
            return self.report_session_closed()

    def get_all_stores(self) -> Response[bool] | Response[str]:
        if self.is_open:
            return self.service.get_all_stores(self.identifier)
        else:
            return self.report_session_closed()

    def get_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return self.service.get_store(self.identifier, store_name)
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

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        if self.is_open:
            return self.service.update_product_quantity(self.identifier, store_name, product_name, quantity)
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

    def show_cart(self) -> Response[bool] | Response[str]:
        if self.is_open:
            return self.service.show_cart(self.identifier)
        else:
            return self.report_session_closed()

    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str) -> Response[bool]:
        if self.is_open:
            return self.service.purchase_shopping_cart(self.identifier, payment_method, payment_details, address, postal_code)
        else:
            return self.report_session_closed()

    def change_product_name(self, store_name: str, product_old_name: str, product_new_name: str):
        if self.is_open:
            return self.service.change_product_name(self.identifier,store_name, product_old_name, product_new_name)
        else:
            return self.report_session_closed()

    def change_product_price(self, store_name: str, product_old_price: float, product_new_price: float):
        if self.is_open:
            return self.service.change_product_price(self.identifier,store_name, product_old_price, product_new_price)
        else:
            return self.report_session_closed()
