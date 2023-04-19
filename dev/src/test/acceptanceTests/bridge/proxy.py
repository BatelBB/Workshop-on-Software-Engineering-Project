import string

from dev.src.test.acceptanceTests.bridge.Bridge import Bridge
from dev.src.test.acceptanceTests.bridge.real import real


class proxy(Bridge):
    real: Bridge

    def __init__(self):
        self.real = real()

    def enter_market(self) -> int:
        if self.real is not None:
            return self.real.enter_market()
        return 1

    def exit_market(self, session_id: int) -> bool:
        if self.real is not None:
            return self.real.exit_market()
        return True

    def register(self, session_id: int, username: string, password: string) -> bool:
        if self.real is not None:
            return self.real.register(session_id, username, password)
        return True

    def login(self, session_id: int, username: string, password: string) -> bool:
        if self.real is not None:
            return self.real.login(session_id, username, password)
        return True







    #guest buying operations
    def get_all_stores(self) -> list:
        return []

    def get_store_products(self, store_id: int) -> list:
        return []

    def get_products_by_name(self, name: string) -> list:
        return []

    def get_products_by_category(self, name: string) -> list:
        return []

    def get_products_by_keyword(self, name: string) -> list:
        return []


    ##quesion??????????????????????????????????????????????????
    def filter_products_by_price_range(self, low: int, high: int) -> list:
        return []

    def filter_products_by_rating(self, low: int, high: int):
        return []

    def filter_products_by_category(self, category: string):
        return []

    def filter_products_by_store_rating(self, low: int, high: int):
        return []

    ##quesion??????????????????????????????????????????????????



    def add_to_cart(self, store_id: int, product_id: int) -> bool:
        return True

    def buy_cart(self) -> bool:
        return True

    #registered user operations
    def logout(self) -> bool:
        return True

    def open_store(self) -> int:
        return 1

    #storeOwner operations
    def add_product(self, store_id: int, product_id: int, amount:  int) -> int:
        return 1

    def remove_product(self, store_id: int, product_id: int, amount:  int) -> bool:
        return True

    def change_product_name(self, store_id: int, product_id: int, new_name: string) -> bool:
        return True

    def change_product_price(self, store_id: int, product_id: int, new_price: int) -> bool:
        return True

    def appoint_owner(self, store_id: int, new_owner: string) -> bool:
        return True

    def appoint_manager(self, store_id: int, new_owner: string) -> bool:
        return True

    #TODO: 4.7: permissions of store manager

    def close_store(self, store_id: int) -> bool:
        return True

    def get_store_personal(self, store_id) -> list:
        return []

    def get_store_purchase_history(self, store_id) -> list:
        return []
