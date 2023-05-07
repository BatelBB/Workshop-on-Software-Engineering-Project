from typing import Any

from dev.src.main.Service import IService
from dev.src.main.Utils.Logger import report_debug, Logger
from dev.src.main.Utils.Response import Response


# At most one member can be logged-in in a session.
class Session:
    def __init__(self, identifier: int, service: IService):
        self.identifier = identifier
        self.service = service
        self.is_open = True

    def __str__(self):
        return f'Session: {self.identifier}'

    def report_debug_session_closed(self, funcName: str) -> Response[bool]:
        return report_debug(f'Attempted to use a closed {self} in function {funcName})', False, Logger.Severity.ERROR)

    def leave(self):
        self.is_open = False
        return report_debug(f'Entered leave function', self.service.leave(self.identifier), Logger.Severity.DEBUG)

    def register(self, username: str, encrypted_password: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered register function with {username} and encrypted password',
                          self.service.register(self.identifier, username, encrypted_password), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.register.__qualname__)

    def is_registered(self, username: str) -> bool:
        return self.is_open and self.service.is_registered(username)

    def login(self, username: str, encrypted_password: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered login function with {username} and encrypted password', 
                          self.service.login(self.identifier, username, encrypted_password), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.login.__qualname__)

    def is_logged_in(self, username: str) -> bool:
        return self.is_open and self.service.is_logged_in(username)

    def logout(self) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered logout function',self.service.logout(self.identifier), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.login.__qualname__)

    def open_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered open store function with name {store_name}', 
                          self.service.open_store(self.identifier, store_name), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.open_store.__qualname__)

    def close_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered close store function with name {store_name}',
                          self.service.close_store(self.identifier, store_name), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.close_store.__qualname__)

    def get_all_stores(self) -> Response[bool] | Response[str]:
        if self.is_open:
            return report_debug(f'Entered get all stores function with no params',
                          self.service.get_all_stores(self.identifier), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_all_stores.__qualname__)

    def get_store(self, store_name: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered get store function with name param {store_name}',
                          self.service.get_store(self.identifier, store_name), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_store.__qualname__)

    def add_product(self, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str] = None) -> Response[bool]:
        if keywords is None:
            keywords = []
        if self.is_open:
            return report_debug(f'Entered add product function with params: \n'
                          f'store name: {store_name}, \n'
                          f'product name: {product_name}, \n'
                          f'category: {category}, \n '
                          f'price: {price}, \n'
                          f'quantity: {quantity}, \n '
                          f'keywords: {keywords}\n',
                          self.service.add_product(self.identifier, store_name, product_name, category, price, quantity,
                                            keywords), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.add_product.__qualname__)

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function update product quantity with params:\n'
                          f'store name: {store_name}, \n'
                          f'product name: {product_name}, \n'
                          f'quantity: {quantity}\n',
                          self.service.update_product_quantity(self.identifier, store_name, product_name, quantity),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.update_product_quantity.__qualname__)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function remove product with params: \n'
                          f'store name: {store_name},  \n'
                          f'product name: {product_name}',
                          self.service.remove_product(self.identifier, store_name, product_name), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.remove_product.__qualname__)

    def add_to_cart(self, store_name: str, product_name: str, quantity: int = 1) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function add_to_cart with params: \n'
                          f'store name: {store_name}, \n'
                          f'product name: {product_name}, \n'
                          f'quantity: {quantity}',
                          self.service.add_to_cart(self.identifier, store_name, product_name, quantity),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.add_to_cart.__qualname__)

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function remove_product_from_cart with params: \n'
                          f'store name: {store_name}, \n'
                          f'product name: {product_name}',
                          self.service.remove_product_from_cart(self.identifier, store_name, product_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.remove_product_from_cart.__qualname__)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function update_cart_product_quantity with params:\n'
                          f'store name: {store_name}, \n'
                          f'product name:{product_name}, \n'
                          f'quantity: {quantity}',
                          self.service.update_cart_product_quantity(self.identifier, store_name, product_name, quantity),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.update_cart_product_quantity.__qualname__)

    def show_cart(self) -> Response[bool] | Response[str]:
        if self.is_open:
            return report_debug(f'Entered function show_cart without params',self.service.show_cart(self.identifier),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.show_cart.__qualname__)

    def purchase_shopping_cart(self, payment_method: str, payment_details: list) -> Response[bool]:
        if self.is_open:
            return report_debug(f'Entered function purchase_shopping_cart with params:\n'
                          f'payment method: {payment_method}, \n'
                          f'payment details: {payment_method}',
                          self.service.purchase_shopping_cart(self.identifier, payment_method, payment_details),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.purchase_shopping_cart.__qualname__)

    def change_product_name(self, store_name: str, product_old_name: str, product_new_name: str):
        if self.is_open:
            return report_debug(f'Entered function change_product_name with params:\n'
                          f'store name: {store_name},\n'
                          f'product old name: {product_old_name}, \n'
                          f'product new name: {product_new_name}',
                          self.service.change_product_name(self.identifier,store_name, product_old_name, product_new_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.change_product_name.__qualname__)

    def change_product_price(self, store_name: str, product_old_price: float, product_new_price: float):
        if self.is_open:
            return report_debug(f'Entered function change_product_price with params:\n'
                          f'store name: {store_name}, \n'
                          f'product old price: {product_old_price}, \n'
                          f'product new price: {product_new_price}',
                          self.service.change_product_price(self.identifier,store_name, product_old_price, product_new_price),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.change_product_price.__qualname__)

    def get_purchase_history(self, store_name:str):
        if self.is_open:
            return report_debug(f'Entered function get_purchase_history with params: \n'
                          f'store name: {store_name}',
                          self.service.get_store_purchase_history(self.identifier, store_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_purchase_history.__qualname__)

    def get_products_by_category(self, category: str):
        if self.is_open:
            return report_debug(f'Entered function get_products_by_category with params:\n'
                          f'category: {category}', self.service.get_products_by_category(self.identifier, category),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_products_by_category.__qualname__)

    def get_products_by_name(self, name: str):
        if self.is_open:
            return report_debug(f'Entered function get_products_by_name with params:\n'
                          f'name: {name}',self.service.get_products_by_name(self.identifier, name),Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_products_by_name.__qualname__)

    def get_products_by_keywords(self, keywords: list[str]):
        if self.is_open:
            return report_debug(f'Entered function get_products_by_keywords with params: keywords: {keywords}',
                          self.service.get_products_by_keywords(self.identifier, keywords), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_products_by_keywords.__qualname__)

    def appoint_owner(self, new_owner_name: str, store_name: str):
        if self.is_open:
            return report_debug(f'Entered function appoint_owner with params: \n'
                          f'new owner name: {new_owner_name},\n'
                          f'store name: {store_name}',
                          self.service.appoint_owner(self.identifier, new_owner_name, store_name), Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.appoint_owner.__qualname__)

    def appoint_manager(self, new_manager_name: str, store_name: str):
        if self.is_open:
            return report_debug(f'Entered function appoint_manager with params: \n'
                          f'new manager name: {new_manager_name},\n'
                          f'store name: {store_name}',
                          self.service.appoint_manager(self.identifier, new_manager_name, store_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.appoint_manager.__qualname__)

    def set_stock_permissions(self, receiving_user_name: str, store_name: str, give_or_take: bool):
        if self.is_open:
            return report_debug(f'Entered function set_stock_permissions with params: \n'
                          f'receiving user name: {receiving_user_name},\n'
                          f'store name: {store_name}, \n'
                          f'give or take: {give_or_take}',
                          self.service.set_stock_permissions(self.identifier, receiving_user_name, store_name, give_or_take),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.set_stock_permissions.__qualname__)

    def set_personal_permissions(self, receiving_user_name: str, store_name: str,
                                 give_or_take: bool):
        if self.is_open:
            return report_debug(f'Entered function set_personal_permissions with params:\n'
                          f'receiving user name: {receiving_user_name}, \n'
                          f'store name: {store_name}, \n'
                          f'give or take: {give_or_take}',
                          self.service.set_personal_permissions(self.identifier, receiving_user_name, store_name, give_or_take),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.set_personal_permissions.__qualname__)

    def get_store_personal(self, store_name: str):
        if self.is_open:
            return report_debug(f'Entered function get_store_personal with params: store name: {store_name}',
                          self.service.get_store_personal(self.identifier, store_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.get_store_personal.__qualname__)

    def fire_employee(self, store_name: str, employee_name: str):
        if self.is_open:
            return report_debug(f'Entered function fire_employee with params: \n'
                          f'store name: {store_name}, \n'
                          f'employee name: {employee_name}',
                          self.service.fire_employee(self.identifier, store_name, employee_name),
                          Logger.Severity.DEBUG)
        else:
            return self.report_debug_session_closed(self.fire_employee.__qualname__)