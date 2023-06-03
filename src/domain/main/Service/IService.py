from abc import ABC, abstractmethod

from reactivex import Observable

from domain.main.Chat.chat_message import ChatMessage
from src.domain.main.Market.Appointment import Appointment
from src.domain.main.Market.Permissions import Permission
from src.domain.main.Store.Product import Product
from src.domain.main.Store.Store import Store
from src.domain.main.User.Cart import Cart
from src.domain.main.Utils.IConcurrentSingelton import IAbsractConcurrentSingleton
from src.domain.main.Utils.Response import Response
from src.domain.main.Utils.Session import Session


class IService(metaclass=IAbsractConcurrentSingleton):
    @abstractmethod
    def enter(self) -> Session:
        ...

    @abstractmethod
    def leave(self, identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def shutdown(self, session_identifier: int) -> Response[bool]:
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
    def get_store(self, session_identifier: int, store_name: str) -> Response[dict | bool]:
        ...

    @abstractmethod
    def get_whole_store(self, session_identifier: int, store_name: str) -> Response[Store | bool]:
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
    def get_all_products_of(self, session_identifier: int, store_name: str) -> Response[set[Product] | bool]:
        ...

    @abstractmethod
    def get_products_by_name(self, session_identifier: int, product_name: str) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_by_category(self, session_identifier: int, category: str) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_by_keywords(self, session_identifier: int, keywords: list[str]) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_in_price_range(self, session_identifier: int, min: float, max: float) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_amount_of(self, session_identifier: int, product_name: str, store_name: str) -> Response[int]:
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
    def show_cart(self, session_identifier: int) -> Response[dict | bool]:
        ...

    @abstractmethod
    def get_cart(self, session_identifier: int) -> Response[Cart]:
        ...

    @abstractmethod
    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list, address: str, postal_code: str) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_name(self, session_identifier: int, store_name: str, product_old_name: str, product_new_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, session_identifier: int, store_name: str, product_old_price: float, product_new_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def appoint_manager(self, session_identifier: int, appointee_name: str, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_owner(self, session_identifier: int,  appointee_name: str, store_name: str) -> Response[bool]:
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
    def reopen_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_personal(self, session_identifier: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def get_store_staff(self, session_identifier: int, store_name: str) -> Response[list[Appointment] | bool]:
        ...

    @abstractmethod
    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str) -> Response[bool]:
        ...

    def start_auction(self, session_id: int, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        ...

    @abstractmethod
    def start_lottery(self, session_id: int, store_name: str, product_name: str) -> Response:
        ...

    @abstractmethod
    def start_bid(self, session_id: int, store_name: str, product_name: str) -> Response:
        ...

    @abstractmethod
    def approve_bid(self, session_id: int, store_name: str, product_name: str, is_approve: bool) -> Response:
        ...

    @abstractmethod
    def add_purchase_simple_rule(self, session_id: int, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        ...

    @abstractmethod
    def add_purchase_complex_rule(self, session_id: int, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str, amount2: int, complex_rule_type: str) -> Response:
        ...

    @abstractmethod
    def cancel_membership_of(self, session_identifier: int, member_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...
    @abstractmethod
    def get_all_registered_users(self) -> list[str]:
        ...

    @abstractmethod
    def add_discount(self, session_id: int, store_name: str, discount_type: str, discount_percent: int,
                     discount_duration: int, discount_for_type: str, discount_for_name: str = None,
                     rule_type=None,
                     discount2_percent=None, discount2_for_type=None, discount2_for_name=None,
                     cond_type: str = None, min_price: float = None,
                     p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        ...

    @abstractmethod
    def get_store_products_with_discounts(self, sessiont_id: int, store_name: str) -> dict[Product:str]:
        ...

    @abstractmethod
    def get_messages_including_past(self, session_id: int,) -> Observable[ChatMessage]:
        ...

    @abstractmethod
    def send_message(self,session_id: int, recipient: str, content: str) -> Response[None]:
        ...
