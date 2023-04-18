import string
from abc import ABC, abstractmethod


class Bridge(ABC):
    @abstractmethod
    def enter_market(self) -> int:
        ...

    #guest
    @abstractmethod
    def exit_market(self) -> bool:
        ...

    @abstractmethod
    def register(self, username: string, password: string) -> bool:
        ...

    @abstractmethod
    def login(self, username: string, password: string) -> bool:
        ...

    #guest buying operations
    @abstractmethod
    def get_all_stores(self) -> list:
        ...

    @abstractmethod
    def get_store_products(self, store_id: int) -> list:
        ...

    @abstractmethod
    def get_products_by_name(self, name: string) -> list:
        ...

    @abstractmethod
    def get_products_by_category(self, name: string) -> list:
        ...

    @abstractmethod
    def get_products_by_keyword(self, name: string) -> list:
        ...


    ##quesion??????????????????????????????????????????????????
    @abstractmethod
    def filter_products_by_price_range(self, low: int, high: int) -> list:
        ...

    @abstractmethod
    def filter_products_by_rating(self, low: int, high: int):
        ...

    @abstractmethod
    def filter_products_by_category(self, category: string):
        ...

    @abstractmethod
    def filter_products_by_store_rating(self, low: int, high: int):
        ...

    ##quesion??????????????????????????????????????????????????



    @abstractmethod
    def add_to_cart(self, store_id: int, product_id: int) -> bool:
        ...

    @abstractmethod
    def buy_cart(self) -> bool:
        ...

    #registered user operations
    @abstractmethod
    def logout(self) -> bool:
        ...

    @abstractmethod
    def open_store(self) -> int:
        ...

    #storeOwner operations
    @abstractmethod
    def add_product(self, store_id: int, product_id: int, amount:  int) -> int:
        ...

    @abstractmethod
    def remove_product(self, store_id: int, product_id: int, amount:  int) -> bool:
        ...

    @abstractmethod
    def change_product_name(self, store_id: int, product_id: int, new_name: string) -> bool:
        ...

    @abstractmethod
    def change_product_price(self, store_id: int, product_id: int, new_price: int) -> bool:
        ...

    @abstractmethod
    def appoint_owner(self, store_id: int, new_owner: string) -> bool:
        ...

    @abstractmethod
    def appoint_manager(self, store_id: int, new_owner: string) -> bool:
        ...

    #TODO: 4.7: permissions of store manager

    @abstractmethod
    def close_store(self, store_id: int) -> bool:
        ...

    @abstractmethod
    def get_store_personal(self, store_id) -> list:
        ...

    @abstractmethod
    def get_store_purchase_history(self, store_id) -> list:
        ...




