from src.domain.main.Utils.Response import Response
from domain.main.bridge.Bridge import Bridge
from domain.main.bridge.real import real
import string

class proxy(Bridge):

    def __init__(self):
        self.real = real()

    def enter_market(self) -> Response[int]:
        if self.real is not None:
            return Response(self.real.enter_market())
        return Response(-1)

    def exit_market(self, session_id: int) -> Response[bool]:
        if self.real is not None:
            return self.real.exit_market(session_id)
        return Response(False)

    def register(self, session_id: int, username: string, password: string) -> Response[bool]:
        if self.real is not None:
            return self.real.register(session_id, username, password)
        return Response(False)

    def login(self, session_id: int, username: string, password: string) -> Response[bool]:
        if self.real is not None:
            return self.real.login(session_id, username, password)
        return Response(False)

    def get_all_stores(self, session_id: int) -> Response[list]:
        if self.real is not None:
            return self.real.get_all_stores(session_id)
        else:
            return Response()

    def remove_product_quantity(self, session_id: int, store_name: str,
                                product_name: str, quantity: int) -> Response[bool]:
        return self.real.remove_product_quantity(session_id, store_name, product_name, quantity)

    def remove_from_cart(self, session_id: int, store_name: str,
                         product_name: str) -> Response[bool]:
        return self.real.remove_from_cart(session_id, store_name, product_name)

    def get_store_products(self, session_id: int, store_name: str) -> Response[dict]:
        if self.real is not None:
            return self.real.get_store_products(session_id, store_name)
        else:
            return Response()

    def get_products_by_name(self, session_id: int, store_name: string) -> Response[dict]:
        if self.real is not None:
            return self.real.get_products_by_name(session_id, store_name)
        else:
            return Response()

    def get_products_by_category(self, session_id: int, store_name: string) -> Response[dict]:
        if self.real is not None:
            return self.real.get_products_by_category(session_id, store_name)
        else:
            return Response()

    def get_products_by_keyword(self, session_id: int, store_name: string) -> Response[dict]:
        if self.real is not None:
            return self.real.get_products_by_keyword(session_id, store_name)
        else:
            return Response()

    def filter_products_by_price_range(self, session_id: int, low: int, high: int) -> Response[dict]:
        if self.real is not None:
            return self.real.filter_products_by_price_range(session_id, low, high)
        else:
            return Response()

    def filter_products_by_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        if self.real is not None:
            return self.real.filter_products_by_rating(session_id, low, high)
        else:
            return Response()

    def filter_products_by_category(self, session_id: int, category: string) -> Response[dict]:
        if self.real is not None:
            return self.real.filter_products_by_category(session_id, category)
        else:
            return Response()

    def filter_products_by_store_rating(self, session_id: int, low: int, high: int) -> Response[dict]:
        if self.real is not None:
            return self.real.filter_products_by_store_rating(session_id, low, high)
        else:
            return Response()

    def add_to_cart(self, session_id: int, store_name: string, product_name: string, quantity: int) -> Response[bool]:
        if self.real is not None:
            return self.real.add_to_cart(session_id, store_name, product_name, quantity)
        return Response()

    def buy_cart_with_card(self, session_id: int, card_num: str, cvv: str, exp_date: str) -> Response[bool]:
        if self.real is not None:
            return self.real.buy_cart_with_card(session_id, card_num, cvv, exp_date)
        return Response()

    def buy_cart_with_paypal(self, session_id: int, username: str, password: str) -> Response[bool]:
        if self.real is not None:
            return self.real.buy_cart_with_paypal(session_id, username, password)
        return Response()

    # registered user operations
    def logout(self, session_id: int,) -> Response[bool]:
        if self.real is not None:
            return self.real.logout(session_id)
        return Response()

    def open_store(self, session_id: int, store_name: string) -> Response[bool]:
        if self.real is not None:
            return self.real.open_store(session_id, store_name)
        return Response()

    # store owner operations
    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        if self.real is not None:
            return self.real.add_product(session_identifier, store_name, product_name, category, price, quantity, keywords)
        return Response()

    def remove_product(self, session_id: int, store_name: str, product_name: str) -> Response[bool]:
        if self.real is not None:
            return self.real.remove_product(session_id, store_name, product_name)
        return Response()

    def change_product_name(self, session_id: int, store_name: str,
                            product_name: str, new_name: string) -> Response[bool]:
        if self.real is not None:
            return self.real.change_product_name(session_id, store_name, product_name, new_name)
        return Response()

    def change_product_price(self, session_id: int, store_name: str, product_name: str, new_price: int) -> Response[bool]:
        if self.real is not None:
            return self.real.change_product_price(session_id, store_name, product_name, new_price)
        return Response()

    def appoint_owner(self, session_id: int, store_name: str, new_owner: string) -> Response[bool]:
        if self.real is not None:
            return self.real.appoint_owner(session_id, store_name, new_owner)
        return Response()

    def appoint_manager(self, session_id: int, store_name: str, new_owner: string) -> Response[bool]:
        if self.real is not None:
            return self.real.appoint_manager(session_id, store_name, new_owner)
        return Response()

    def set_stock_permission(self, session_id: int, receiving_user_name: str,
                             store_name: str, give_or_take: bool) -> Response[bool]:
        return self.real.set_stock_permission(session_id, receiving_user_name, store_name, give_or_take)

    def set_personal_permissions(self, session_id: int, receiving_user_name: str,
                                 store_name: str, give_or_take: bool) -> Response[bool]:
        return self.real.set_personal_permissions(session_id, receiving_user_name, store_name, give_or_take)

    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        if self.real is not None:
            return self.real.close_store(session_id, store_name)
        return Response()

    def get_store_personal(self, session_id: int, store_name: str) -> Response[dict]:
        if self.real is not None:
            return self.real.get_store_personal(session_id, store_name)
        return Response()

    def get_store_purchase_history(self, session_id: int, store_name: str) -> Response[dict]:
        if self.real is not None:
            return self.real.get_store_purchase_history(session_id, store_name)
        return Response()

    def show_cart(self, session_id: int) -> Response[dict]:
        if self.real is not None:
            return self.real.show_cart(session_id)
        return Response()