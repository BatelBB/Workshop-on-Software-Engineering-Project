import json
import os
from typing import Any, List

from reactivex import Observable

from src.domain.main.Notifications.notification import Notification
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.Market.Appointment import Appointment
from src.domain.main.Market.Permissions import Permission
from Service.IService import IService
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.Store import Store
from src.domain.main.UserModule.Cart import Cart
from src.domain.main.Utils.Logger import report, Logger, report_error
from src.domain.main.Utils.Response import Response


# At most one member can be logged-in in a session.
class Session:
    def __init__(self, identifier: int, service: IService):
        self.identifier = identifier
        self.service: IService = service
        self.is_open = True
        self.load_configuration()

    def __str__(self):
        return f'Session: {self.identifier}'

    def report_session_closed(self) -> Response[bool]:
        return report(f'Attempted to use a closed {self})', False, Logger.Severity.ERROR)

    def apply(self, f, *args, g=report_session_closed) -> Any:
        return f(*args) if self.is_open else g()

    def leave(self) -> Response[bool]:
        self.is_open = False
        return self.service.leave(self.identifier)

    def shutdown(self) -> Response[bool]:
        return self.service.shutdown(self.identifier)

    def register(self, username: str, password: str) -> Response[bool]:
        return self.apply(self.service.register, self.identifier, username, password)

    def register_admin(self, username: str, password: str, is_admin: bool = True) -> Response[bool]:
        return self.apply(self.service.register, self.identifier, username, password, is_admin)

    def is_registered(self, username: str) -> bool:
        return self.apply(self.service.is_registered, username)

    def login(self, username: str, encrypted_password: str) -> Response[bool]:
        return self.apply(self.service.login, self.identifier, username, encrypted_password)

    def is_logged_in(self, username: str) -> bool:
        return self.apply(self.service.is_logged_in, username)

    def logout(self) -> Response[bool]:
        return self.apply(self.service.logout, self.identifier)

    def open_store(self, store_name: str) -> Response[bool]:
        return self.apply(self.service.open_store, self.identifier, store_name)

    def remove_store(self, store_name: str) -> Response[bool]:
        return self.apply(self.service.remove_store, self.identifier, store_name)

    def get_all_stores(self) -> Response[list[Store] | bool]:
        return self.apply(self.service.get_all_stores, self.identifier)

    def get_all_deleted_stores(self) -> Response[list[Store] | bool]:
        return self.apply(self.service.get_all_deleted_stores, self.identifier)

    def get_store(self, store_name: str) -> Response[dict | bool]:
        return self.apply(self.service.get_store, self.identifier, store_name)

    def get_whole_store(self, store_name: str) -> Response[Store | bool]:
        return self.apply(self.service.get_whole_store, self.identifier, store_name)

    def get_all_products_of(self, store_name: str) -> Response[set[Product] | bool]:
        return self.apply(self.service.get_all_products_of, self.identifier, store_name)

    def get_products_by_name(self, product_name: str) -> Response[list[dict[str, dict]] | bool]:
        return self.apply(self.service.get_products_by_name, self.identifier, product_name)

    def get_products_by_category(self, category: str) -> Response[list[dict[str, dict]] | bool]:
        return self.apply(self.service.get_products_by_category, self.identifier, category)

    def get_products_by_keywords(self, keywords: list[str]) -> Response[list[dict[str, dict]] | bool]:
        return self.apply(self.service.get_products_by_keywords, self.identifier, keywords)

    def get_products_in_price_range(self, min: float, max: float) -> Response[list[dict[str, dict]] | bool]:
        return self.apply(self.service.get_products_in_price_range, self.identifier, min, max)

    def add_product(self, store_name: str, product_name: str, category: str, price: float, quantity: int,
                    keywords: list[str] = None) -> Response[bool]:
        return self.apply(self.service.add_product, self.identifier, store_name, product_name, category, float(price),
                          int(quantity), keywords)

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.apply(self.service.update_product_quantity, self.identifier, store_name, product_name, quantity)

    def get_amount_of(self, product_name: str, store_name: str) -> Response[int]:
        return self.apply(self.service.get_amount_of, self.identifier, product_name, store_name)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.apply(self.service.remove_product, self.identifier, store_name, product_name)

    def add_to_cart(self, store_name: str, product_name: str, quantity: int = 1) -> Response[bool]:
        return self.apply(self.service.add_to_cart, self.identifier, store_name, product_name, quantity)

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        return self.apply(self.service.remove_product_from_cart, self.identifier, store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.apply(self.service.update_cart_product_quantity, self.identifier, store_name, product_name,
                          quantity)

    def show_cart(self) -> Response[dict | bool]:
        return self.apply(self.service.show_cart, self.identifier)

    def get_cart(self) -> Response[Cart]:
        return self.apply(self.service.get_cart, self.identifier)

    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str,
                               city: str, country: str) -> Response[bool]:
        return self.apply(self.service.purchase_shopping_cart, self.identifier, payment_method, payment_details,
                          address, postal_code, city, country)

    def close_store(self, store_name: str) -> Response[bool]:
        return self.apply(self.service.close_store, self.identifier, store_name)

    def appoint_manager(self, appointee: str, store: str, ) -> Response[bool]:
        return self.apply(self.service.appoint_manager, self.identifier, appointee, store)

    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        return self.apply(self.service.appoint_owner, self.identifier, appointee, store)

    def approve_owner(self, appointee: str, store: str, is_approve: bool) -> Response[bool]:
        return self.apply(self.service.approve_owner, self.identifier, appointee, store, is_approve)

    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        return self.apply(self.service.appointees_at, self.identifier, store)

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        return self.apply(self.service.remove_appointment, self.identifier, fired_appointee, store_name)

    def add_permission(self, store: str, appointee: str, permission: Permission | str) -> Response[bool]:
        if isinstance(permission, str):
            permission = getattr(Permission, permission)
        return self.apply(self.service.add_permission, self.identifier, store, appointee, permission)

    def remove_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        if isinstance(permission, str):
            permission = getattr(Permission, permission)
        return self.apply(self.service.remove_permission, self.identifier, store, appointee, permission)

    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        return self.apply(self.service.permissions_of, self.identifier, store, subject)

    def get_admin_permissions(self) -> Response[set[Permission] | bool]:
        return self.apply(self.service.get_admin_permissions)

    def reopen_store(self, store_name: str) -> Response[bool]:
        return self.apply(self.service.reopen_store, self.identifier, store_name)

    def get_store_staff(self, store_name: str) -> Response[list[Appointment] | bool]:
        return self.apply(self.service.get_store_staff, self.identifier, store_name)

    def get_store_personal(self, store_name: str) -> Response[str]:
        return self.apply(self.service.get_store_personal, self.identifier, store_name)

    def change_product_name(self, store_name: str, product_old_name: str, product_new_name: str) -> Response[bool]:
        return self.apply(self.service.change_product_name, self.identifier, store_name, product_old_name,
                          product_new_name)

    def change_product_price(self, store_name: str, product_old_price: float, product_new_price: float) -> Response[
        bool]:
        return self.apply(self.service.change_product_price, self.identifier, store_name, product_old_price,
                          product_new_price)

    def change_product_category(self, store_name: str, old_product_name: str, category: str) -> Response[bool]:
        return self.apply(self.service.change_product_category, self.identifier, store_name, old_product_name, category)

    def get_store_purchase_history(self, store_name: str) -> Response[str]:
        return self.apply(self.service.get_store_purchase_history, self.identifier, store_name)

    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str) -> Response[
        bool]:
        return self.apply(self.service.purchase_with_non_immediate_policy, self.identifier, store_name, product_name,
                          payment_method,
                          payment_details, address, postal_code, how_much, city, country)

    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        return self.apply(self.service.start_auction, self.identifier, store_name, product_name, initial_price,
                          duration)

    def start_lottery(self, store_name: str, product_name: str) -> Response:
        return self.apply(self.service.start_lottery, self.identifier, store_name, product_name)

    def start_bid(self, store_name: str, product_name: str) -> Response:
        return self.apply(self.service.start_bid, self.identifier, store_name, product_name)

    def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response:
        return self.apply(self.service.approve_bid, self.identifier, store_name, product_name, is_approve)

    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        return self.apply(self.service.add_purchase_simple_rule, self.identifier, store_name, product_name, gle, amount)

    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str,
                                  amount2: int, complex_rule_type: str) -> Response:
        return self.apply(self.service.add_purchase_complex_rule, self.identifier, store_name, p1_name, gle1, amount1,
                          p2_name, gle2, amount2, complex_rule_type)

    def cancel_membership_of(self, member_name: str) -> Response[bool]:
        return self.apply(self.service.cancel_membership_of, self.identifier, member_name)

    def get_all_registered_users(self) -> list[str]:
        return self.apply(self.service.get_all_registered_users)

    def add_simple_discount(self, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None,
                            rule_type=None, min_price: float = None,
                            p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) -> Response:
        return self.apply(self.service.add_simple_discount, self.identifier, store_name, discount_type,
                          discount_percent, discount_for_name, rule_type, min_price, p1_name, gle1,
                          amount1, p2_name, gle2, amount2)

    def connect_discounts(self, store_name, id1, id2, connection_type, rule_type=None,
                          min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        return self.apply(self.service.connect_discounts, self.identifier, store_name, id1, id2, connection_type,
                          rule_type, min_price, p1_name, gle1, amount1, p2_name, gle2, amount2)

    def get_purchase_rules(self, store_name: str) -> Response[dict[int:IRule]]:
        return self.apply(self.service.get_purchase_rules, self.identifier, store_name)

    def delete_purchase_rule(self, index, store_name):
        return self.apply(self.service.delete_purchase_rule, self.identifier, store_name, index)

    def add_basket_purchase_rule(self, store_name: str, min_price: float) -> Response:
        return self.apply(self.service.add_basket_purchase_rule, self.identifier, store_name, min_price)

    def get_discounts(self, store_name: str) -> Response:
        return self.apply(self.service.get_discounts, self.identifier, store_name)

    def delete_discount(self, store_name: str, index: int):
        return self.apply(self.service.delete_discount, self.identifier, store_name, index)

    def dispatch(self, action_name, *args):
        actions = {"register": self.register, "login": self.login, "open_store": self.open_store,
                   "appoint_owner": self.appoint_owner, "logout": self.logout,
                   "add_product": self.add_product, "appoint_manager": self.appoint_manager,
                   "add_permission": self.add_permission, "register_admin": self.register_admin,
                   "get_store_staff": self.get_store_staff}

        return actions[action_name](*args) if action_name in actions \
            else report_error(self.dispatch.__qualname__, f'Invalid action. Given: {action_name}.')

    def get_store_owners(self, store_name: str):
        return self.apply(self.service.get_store_owners, self.identifier, store_name)

    def get_store_managers(self, store_name: str):
        return self.apply(self.service.get_store_managers, self.identifier, store_name)

    def get_cart_price(self, baskets):
        return self.apply(self.service.get_cart_price, baskets)

    def get_number_of_registered_users(self) -> int:
        return self.apply(self.service.get_number_of_registered_users)

    def get_number_of_stores(self) -> int:
        return self.apply(self.service.get_number_of_stores)

    def send_message(self, recipient, content):
        return self.apply(self.service.send_user_message, self.identifier, recipient, content)

    @property
    def unread_amount_observable(self) -> Response[Observable[Notification]]:
        return self.apply(self.service.get_user_unread_observable, self.identifier)

    def get_inbox(self) -> Response[List[Notification]]:
        return self.apply(self.service.get_inbox, self.identifier)

    def mark_read(self, msg_id: int):
        return self.apply(self.service.mark_read, self.identifier, msg_id)

    def get_approval_lists_for_store(self, store_name) -> Response:
        return self.apply(self.service.get_approval_lists_for_store, self.identifier, store_name)

    def get_store_staff_wit_permissions(self, store_name: str):
        return self.apply(self.service.get_store_staff_wit_permissions, self.identifier, store_name)

    def load_configuration(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))  # get the directory of the current script
        config_path = os.path.join(dir_path, '..', '..', '..', 'Configuration',
                                   'config.json')  # construct the path to config.json
        config_path = os.path.abspath(config_path)  # resolve the path
        with open(config_path, 'r') as f:
            config = json.load(f)
        return self.apply(self.service.load_configuration, config)

    def is_admin(self):
        return self.apply(self.service.is_admin, self.identifier)

    def get_bid_products(self, store_name: str) -> Response[dict | bool]:
        return self.apply(self.service.get_bid_products, self.identifier, store_name)
