from src.domain.main.Utils.Response import Response
from domain.main.bridge.Bridge import Bridge
from src.domain.main.Market.Market import Market
import string


class real(Bridge):
    market: Market
    user_sessions: list[int]
    user_counter: int

    def __init__(self):
        self.user_sessions = []
        self.market = Market()
        self.user_counter = 0

    def enter_market(self) -> int:
        s = self.market.enter()
        self.user_sessions.append(s.identifier)
        return s.identifier

    def register(self, session_id: int, username: string, password: string) -> Response[bool]:
        return self.market.register(session_id, username, password)

    def exit_market(self, session_id: int) -> Response[bool]:
        return self.market.exit_market(session_id)

    def login(self, session_id: int, username: string, password: string) -> Response[bool]:
        return self.market.login(session_id, username, password)

    def open_store(self, session_id: int, store_name: string) -> Response[bool]:
        return self.market.open_store(session_id, store_name)

    # todo change name signature
    def remove_product_quantity(self, session_id: int, store_name: str,
                                product_name: str, quantity: int) -> Response[bool]:
        return self.market.update_product_quantity(session_id, store_name, product_name, quantity)

    # guest buying operations
    def remove_from_cart(self, session_id: int, store_name: string,
                         product_name: string) -> Response[bool]:
        return self.market.remove_product_from_cart(session_id, store_name, product_name)

    def get_all_stores(self, session_id) -> Response[list]:
        return self.market.get_all_stores(session_id)

    def get_store_products(self, session_id: int, store_name: str) -> Response[dict]:
        return self.market.get_store(session_id, store_name)

    def get_products_by_name(self, session_id: int, name: string) -> Response[dict]:
        return self.market.get_product_by_name(session_id, name)

    def get_products_by_category(self, session_id: int, name: string) -> Response[dict]:
        return self.market.get_product_by_category(session_id, name)

    def get_products_by_keyword(self, session_id: int, name: string) -> Response[dict]:
        return self.market.get_product_by_keywords(session_id, name)

    def filter_products_by_price_range(self, session_id: int, low: int, high: int) -> Response[dict]:
        return self.market.filter_products_by_price_range(session_id, low, high)

    def filter_products_by_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        return self.market.filter_products_by_rating(session_id, low, high)

    def filter_products_by_category(self, session_id: int, category: string) -> Response[dict]:
        return self.market.filter_products_by_category(session_id, category)

    def filter_products_by_store_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        return self.market.filter_products_by_category(session_id, low, high)

    def add_to_cart(self, session_id: int, store_name: string, product_name: string, quantity: int) -> Response[bool]:
        return self.market.add_to_cart(session_id, store_name, product_name, quantity)

    def buy_cart_with_card(self, session_id: int, card_num: str, cvv: str, exp_date: str, address: str, postal_code: str) -> Response[bool]:
        return self.market.purchase_shopping_cart(session_id, "card", [card_num, cvv, exp_date], address, postal_code)

    def buy_cart_with_paypal(self, session_id: int, username: str, password: str, address: str, postal_code: str) -> Response[bool]:
        return self.market.purchase_shopping_cart(session_id, "paypal", [username, password], address, postal_code)

    # registered user operations
    def logout(self, session_id: int, ) -> Response[bool]:
        return self.market.logout(session_id)

    # storeOwner operations
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        return self.market.add_product(session_identifier, store_name, product_name,
                                       category, price, quantity, keywords)

    def remove_product(self, session_id: int, store_name: str, product_name: str) -> Response[bool]:
        return self.market.remove_product(session_id, store_name, product_name)

    def change_product_name(self, session_id: int, store_name: str,
                            product_name: str, new_name: string) -> Response[bool]:
        return self.market.change_product_name(session_id, store_name, product_name, new_name)

    def change_product_price(self, session_id: int, store_name: str,
                             product_name: str, new_price: float) -> Response[bool]:
        return self.market.change_product_price(session_id, store_name, product_name, new_price)

    def appoint_owner(self, session_id: int, store_name: str, new_owner: string) -> Response[bool]:
        return self.market.appoint_owner(session_id, store_name, new_owner)

    def appoint_manager(self, session_id: int, store_name: str, new_manager: string) -> Response[bool]:
        return self.market.appoint_owner(session_id, store_name, new_manager)

    def set_stock_permission(self, session_id: int, receiving_user_name: str,
                             store_name: str, give_or_take: bool) -> Response[bool]:
        return self.market.set_stock_permissions(session_id, receiving_user_name, store_name, give_or_take)

    def set_personal_permissions(self, session_id: int, receiving_user_name: str,
                                 store_name: str, give_or_take: bool) -> Response[bool]:
        return self.market.set_personal_permissions(session_id, receiving_user_name, store_name, give_or_take)

    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        return self.market.close_store(session_id, store_name)

    def get_store_personal(self, session_id: int, store_name: str) -> Response[dict]:
        return self.market.get_store_personal(session_id, store_name)

    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[dict]:
        return self.market.get_store_purchase_history(session_id, store_name)

    def show_cart(self, session_id: int) -> Response[dict]:
        return self.market.show_cart(session_id)
