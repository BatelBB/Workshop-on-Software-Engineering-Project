from dev.src.main.Utils.Response import Response
from dev.src.main.bridge.Bridge import Bridge
from dev.src.main.bridge.real import real
import string

class proxy(Bridge):
    real: Bridge

    def __init__(self):
        self.real = real()

    def remove_product_quantity(self, session_id: int, store_name: str,
                                product_name: str, quantity: int) -> Response[bool]:
        return real.remove_product_quantity(session_id, store_name, product_name, quantity)

    def remove_from_cart(self, session_id: int, store_name: string,
                         product_name: string, quantity: int) -> Response[bool]:
        return real.remove_product_quantity(session_id, store_name, product_name, quantity)

    def enter_market(self) -> int:
        if self.real is not None:
            return self.real.enter_market()
        return 1

    def exit_market(self, session_id: int) -> bool:
        if self.real is not None:
            return self.real.exit_market(session_id)
        return True

    def register(self, session_id: int, username: string, password: string) -> bool:
        if self.real is not None:
            return self.real.register(session_id, username, password)
        return True

    def login(self, session_id: int, username: string, password: string) -> bool:
        if self.real is not None:
            return self.real.login(session_id, username, password)
        return True

    def get_all_stores(self, session_id: int) -> list:
        if self.real is not None:
            return self.real.get_all_stores(session_id)
        else:
            return []

    def get_store_products(self, session_id: int, store_name: str) -> list:
        if self.real is not None:
            return self.real.get_store_products(session_id, store_name)
        else:
            return []

    def get_products_by_name(self, session_id: int, store_name: string) -> list:
        if self.real is not None:
            return self.real.get_products_by_name(session_id, store_name)
        else:
            return []

    def get_products_by_category(self, session_id: int, store_name: string) -> list:
        if self.real is not None:
            return self.real.get_products_by_category(session_id, store_name)
        else:
            return []

    def get_products_by_keyword(self, session_id: int, store_name: string) -> list:
        if self.real is not None:
            return self.real.get_products_by_keyword(session_id, store_name)
        else:
            return []

    def filter_products_by_price_range(self, session_id: int, low: int, high: int) -> list:
        if self.real is not None:
            return self.real.filter_products_by_price_range(session_id, low, high)
        else:
            return []

    def filter_products_by_rating(self, session_id: int, low: int, high: int):
        if self.real is not None:
            return self.real.filter_products_by_rating(session_id, low, high)
        else:
            return []

    def filter_products_by_category(self, session_id: int, category: string):
        if self.real is not None:
            return self.real.filter_products_by_category(session_id, category)
        else:
            return []

    def filter_products_by_store_rating(self, session_id: int, low: int, high: int):
        if self.real is not None:
            return self.real.filter_products_by_store_rating(session_id, low, high)
        else:
            return []

    def add_to_cart(self, session_id: int, store_name: string, product_name: string, quantity: int) -> bool:
        if self.real is not None:
            return self.real.add_to_cart(session_id, store_name, product_name, quantity)
        return True

    def buy_cart_with_card(self, session_id: int, card_num: str, cvv: str, exp_date: str) -> bool:
        if self.real is not None:
            return self.real.buy_cart_with_card(session_id, card_num, cvv, exp_date)
        return True

    def buy_cart_with_paypal(self, session_id: int, username: str, password: str) -> bool:
        if self.real is not None:
            return self.real.buy_cart_with_paypal(session_id, username, password)
        return True

    # registered user operations
    def logout(self, session_id: int,) -> bool:
        if self.real is not None:
            return self.real.logout(session_id)
        return True

    def open_store(self, session_id: int, store_name: string) -> bool:
        if self.real is not None:
            return self.real.open_store(session_id, store_name)
        return True

    # store owner operations
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> bool:
        if self.real is not None:
            return self.real.add_product(session_identifier, store_name, product_name, category, price, quantity, keywords)
        return True

    def remove_product(self, session_id: int, store_name: str, product_name: str) -> bool:
        if self.real is not None:
            return self.real.remove_product(session_id, store_name, product_name)
        return True

    def change_product_name(self, session_id: int, store_name: str, product_name: str, new_name: string) -> bool:
        if self.real is not None:
            return self.real.change_product_name(session_id, store_name, product_name, new_name)
        return True

    def change_product_price(self, session_id: int, store_name: str, product_name: str, new_price: int) -> bool:
        if self.real is not None:
            return self.real.change_product_price(session_id, store_name, product_name, new_price)
        return True

    def appoint_owner(self, session_id: int, store_name: str, new_owner: string) -> bool:
        if self.real is not None:
            return self.real.appoint_owner(session_id, store_name, new_owner)
        return True

    def appoint_manager(self, session_id: int, store_name: str, new_owner: string) -> bool:
        if self.real is not None:
            return self.real.appoint_manager(session_id, store_name, new_owner)
        return True

    #TODO: 4.7: permissions of store manager
    def close_store(self, session_id: int, store_name: str) -> bool:
        if self.real is not None:
            return self.real.close_store(session_id, store_name)
        return True

    def get_store_personal(self, session_id: int, store_name: str) -> list:
        if self.real is not None:
            return self.real.get_store_personal(session_id, store_name)
        return []

    def get_store_purchase_history(self, session_id: int, store_name: str) -> list:
        if self.real is not None:
            return self.real.get_store_purchase_history(session_id, store_name)
        return []

    def show_cart(self, session_id: int) -> list:
        if self.real is not None:
            return self.real.show_cart(session_id)
        return []