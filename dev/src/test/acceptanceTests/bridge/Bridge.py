import string
from abc import ABC, abstractmethod


class Bridge(ABC):
    @abstractmethod
    def enter_market(self) -> int:
        ...

    #guest
    @abstractmethod
    def exit_market(self, session_id: int) -> bool:
        ...

    @abstractmethod
    def register(self, session_id: int, username: string, password: string) -> bool:
        ...

    @abstractmethod
    def login(self, session_id: int, username: string, password: string) -> bool:
        ...

    #guest buying operations
    @abstractmethod
    def get_all_stores(self, session_id: int) -> list:
        ...

    @abstractmethod
    def get_store_products(self, session_id: int, store_id: int) -> list:
        ...

    @abstractmethod
    def get_products_by_name(self, session_id: int, name: string) -> list:
        ...

    @abstractmethod
    def get_products_by_category(self, session_id: int, name: string) -> list:
        ...

    @abstractmethod
    def get_products_by_keyword(self, session_id: int, name: string) -> list:
        ...


    ##quesion??????????????????????????????????????????????????
    @abstractmethod
    def filter_products_by_price_range(self, session_id: int, low: int, high: int) -> list:
        ...

    @abstractmethod
    def filter_products_by_rating(self, session_id: int, low: int, high: int):
        ...

    @abstractmethod
    def filter_products_by_category(self, session_id: int, category: string):
        ...

    @abstractmethod
    def filter_products_by_store_rating(self, session_id: int, low: int, high: int):
        ...

    ##quesion??????????????????????????????????????????????????



    @abstractmethod
    def add_to_cart(self, session_id: int, store_name: string, product_name: string, quantity: int) -> bool:
        ...

    @abstractmethod
    def buy_cart(self, session_id: int,) -> bool:
        ...

    #registered user operations
    @abstractmethod
    def logout(self, session_id: int,) -> bool:
        ...

    @abstractmethod
    def open_store(self, session_id: int, store_name: string) -> bool:
        ...

    #storeOwner operations
    @abstractmethod
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> bool:
        ...

    @abstractmethod
    def remove_product(self, session_id: int, store_id: int, product_id: int, amount:  int) -> bool:
        ...

    @abstractmethod
    def change_product_name(self, session_id: int, store_id: int, product_id: int, new_name: string) -> bool:
        ...

    @abstractmethod
    def change_product_price(self, session_id: int, store_id: int, product_id: int, new_price: int) -> bool:
        ...

    @abstractmethod
    def appoint_owner(self, session_id: int, store_id: int, new_owner: string) -> bool:
        ...

    @abstractmethod
    def appoint_manager(self, session_id: int, store_id: int, new_owner: string) -> bool:
        ...

    #TODO: 4.7: permissions of store manager

    @abstractmethod
    def close_store(self, session_id: int, store_id: int) -> bool:
        ...

    @abstractmethod
    def get_store_personal(self, session_id: int, store_id) -> list:
        ...

    @abstractmethod
    def get_store_purchase_history(self, session_id: int, store_id) -> list:
        ...

    @abstractmethod
    def show_cart(self, session_id: int) -> list:
        ...


