from abc import ABC, abstractmethod
from dev.src.main.Utils.Response import Response
from dev.src.main.Utils.Session import Session


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

    @abstractmethod
    def get_all_stores(self, session_identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def get_store(self, session_identifier: int, store_name: str) -> Response[bool]:
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
    def show_cart(self, session_identifier: int) -> Response[bool]:
        ...

    @abstractmethod
    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_products(self, session_id: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def change_product_name(self, session_id: int, store_name: str, product_old_name: str, product_new_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, session_id: int, store_name: str, product_old_price: float, product_new_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[str]:
        ...

    @abstractmethod
    def appoint_manager(self, session_id: int, store_name: str, new_manager_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_owner(self, session_id: int, new_owner_name: str, store_name: str) -> Response[bool]:
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
