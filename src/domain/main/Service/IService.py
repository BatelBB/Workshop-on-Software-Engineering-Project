from abc import ABC, abstractmethod
from src.domain.main.Utils.Response import Response
from src.domain.main.Utils.Session import Session


class IService(ABC):
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

    @abstractmethod
    def get_all_stores(self, session_identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def get_store(self, session_identifier: int, store_name: str) -> Response[dict] | Response[bool]:
        ...

    @abstractmethod
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        ...

    @abstractmethod
    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> \
            Response[bool]:
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
    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str,
                                     quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def show_cart(self, session_identifier: int) -> Response[dict] | Response[bool]:
        ...

    @abstractmethod
    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list, address: str,
                               postal_code: str) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_name(self, session_id: int, store_name: str, product_old_name: str, product_new_name: str) -> \
            Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, session_id: int, store_name: str, product_old_price: float,
                             product_new_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def appoint_manager(self, session_id: int, new_manager_name: str, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_products_by_category(self, session_id: int, category: str) -> Response[dict]:
        ...

    @abstractmethod
    def appoint_owner(self, session_id: int, new_owner_name: str, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_products_by_name(self, session_id: int, name: str) -> Response[dict]:
        ...

    @abstractmethod
    def get_products_by_keywords(self, session_id: int, keywords: list[str]) -> Response[dict]:
        ...

    @abstractmethod
    def set_stock_permissions(self, session_id: int, receiving_user_name: str, store_name: str, give_or_take: bool) -> \
            Response[bool]:
        ...

    @abstractmethod
    def set_personal_permissions(self, session_id: int, receiving_user_name: str, store_name: str,
                                 give_or_take: bool) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_personal(self, session_id: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float) -> Response[bool]:
        ...

    def start_auction(self, session_id: int, store_name: str, product_name: str, initial_price: float, duration: int) -> \
    Response[bool]:
        ...

    @abstractmethod
    def start_lottery(self, session_id: int, store_name: str, product_name: str) -> \
            Response:
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
    def add_purchase_complex_rule(self, session_id: int, store_name: str, p1_name: str, gle1: str, amount1: int,
                                  p2_name: str, gle2: str, amount2: int,
                                  complex_rule_type: str) -> Response:
        ...
    # @abstractmethod
    # def update_product_of(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
    #     ...

    # @abstractmethod
    # def get_product_by_name(self, session_identifier: int, product_name: str) -> Response[str]:
    #     ...
    #
    # @abstractmethod
    # def get_products_by_category(self, session_identifier: int, product_category: str) -> Response[str]:
    #     ...
    #
    # @abstractmethod
    # def get_products_by_keywords(self, session_identifier: int, product_keywords: list[str]) -> Response[str]:
    #     ...