from abc import ABC, abstractmethod
from dev.src.main.Utils.Response import Response
import string


class Bridge(ABC):
    def enter_market(self) -> int:
        ...

    @abstractmethod
    def register(self, session_id: int, username: string, password: string) -> Response[bool]:
        ...

    @abstractmethod
    def exit_market(self, session_id: int) -> Response[bool]:
        ...

    @abstractmethod
    def login(self, session_id: int, username: string, password: string) -> Response[bool]:
        ...

    @abstractmethod
    def open_store(self, session_id: int, store_name: string) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product_quantity(self, session_id: int, store_name: str,
                                product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def remove_from_cart(self, session_id: int, store_name: string,
                         product_name: string) -> Response[bool]:
        ...

    @abstractmethod
    def get_all_stores(self, session_id) -> Response[list]:
        ...

    @abstractmethod
    def get_store_products(self, session_id: int, store_name: str) -> Response[dict]:
        ...

    @abstractmethod
    def get_products_by_name(self, session_id: int, name: string) -> Response[dict]:
        ...

    @abstractmethod
    def get_products_by_category(self, session_id: int, name: string) -> Response[dict]:
        ...

    @abstractmethod
    def get_products_by_keyword(self, session_id: int, name: string) -> Response[dict]:
        ...

    @abstractmethod
    def filter_products_by_price_range(self, session_id: int, low: int, high: int) -> Response[dict]:
        ...

    @abstractmethod
    def filter_products_by_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        ...

    @abstractmethod
    def filter_products_by_category(self, session_id: int, category: string) -> Response[dict]:
        ...

    @abstractmethod
    def filter_products_by_store_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        ...

    @abstractmethod
    def add_to_cart(self, session_id: int, store_name: string, product_name: string, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def buy_cart_with_card(self, session_id: int, card_num: str, cvv: str, exp_date: str) -> Response[bool]:
        ...

    @abstractmethod
    def buy_cart_with_paypal(self, session_id: int, username: str, password: str) -> Response[bool]:
        ...

    @abstractmethod
    # registered user operations
    def logout(self, session_id: int, ) -> Response[bool]:
        ...

    @abstractmethod
    # storeOwner operations
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product(self, session_id: int, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_name(self, session_id: int, store_name: str,
                            product_name: str, new_name: string) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, session_id: int, store_name: str,
                             product_name: str, new_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_owner(self, session_id: int, store_name: str, new_owner: string) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_manager(self, session_id: int, store_name: str, new_manager: string) -> Response[bool]:
        ...

    @abstractmethod
    def set_stock_permission(self, session_id: int, receiving_user_name: str,
                             store_name: str, give_or_take: bool) -> Response[bool]:
        ...

    @abstractmethod
    def set_personal_permissions(self, session_id: int, receiving_user_name: str,
                                 store_name: str, give_or_take: bool) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_personal(self, session_id: int, store_name: str) -> Response[dict]:
        ...

    @abstractmethod
    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[dict]:
        ...

    @abstractmethod
    def show_cart(self, session_id: int) -> Response[dict]:
        ...




