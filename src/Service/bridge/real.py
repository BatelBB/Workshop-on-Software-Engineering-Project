from domain.main.Market.Permissions import Permission
from Service.IService.IService import IService
from Service.Session.Session import Session
from src.domain.main.Utils.Response import Response
from Service.bridge.Bridge import Bridge
from src.domain.main.Market.Market import Market


class Real(Bridge):
    market: IService
    session: Session

    def __init__(self):
        self.market = Market()

    ###################
    # general services
    def enter_market(self):
        session = self.market.enter()

    def exit_market(self) -> Response[bool]:
        return self.session.leave()
    
    def register(self, username: str, password: str) -> Response[bool]:
        return self.session.register(username, password)
    
    def login(self, username: str, password: str) -> Response[bool]:
        return self.session.login(username, password)
    
    def logout(self) -> Response[bool]:
        return self.session.logout()

    #########################
    # user purchase services
    def add_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.session.add_to_cart(store_name, product_name, quantity)
    
    def remove_from_cart(self, store_name: str,
                         product_name: str) -> Response[bool]:
        return self.session.remove_product_from_cart(store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.session.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> Response[dict | bool]:
        return self.session.show_cart()
    
    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str) \
            -> Response[bool]:
        return self.session.purchase_shopping_cart(payment_method, payment_details, address, postal_code)
    
    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str) -> Response[bool]:
        return self.session.purchase_with_non_immediate_policy(store_name, product_name, payment_method,
                                                               payment_details, address, postal_code, how_much, city,
                                                               country)

    ##############################
    # store management services
    def open_store(self, store_name: str) -> Response[bool]:
        return self.session.open_store(store_name)
    
    def close_store(self, store_name: str) -> Response[bool]:
        return self.session.close_store(store_name)

    def reopen_store(self, store_name: str) -> Response[bool]:
        return self.session.reopen_store(store_name)
    
    def add_product(self, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str] = None) -> Response[bool]:
        return self.session.add_product(store_name, product_name, category, price, quantity, keywords)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.session.remove_product(store_name, product_name)
    
    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.session.update_product_quantity(store_name, product_name, quantity)
    
    def change_product_name(self, store_name: str,
                            product_name: str, new_name: str) -> Response[bool]:
        return self.session.change_product_name(store_name, product_name, new_name)
    
    def change_product_price(self, store_name: str,
                             product_price: float, new_price: float) -> Response[bool]:
        return self.session.change_product_price(store_name, product_price, new_price)

    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        return self.session.appoint_owner(appointee, store)
    
    def appoint_manager(self, appointee: str, store: str) -> Response[bool]:
        return self.session.appoint_manager(appointee, store)
    
    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        return self.session.appointees_at(store)

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        return self.session.remove_appointment(fired_appointee, store_name)

    def add_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.session.add_permission(store, appointee, permission)
    
    def remove_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.session.remove_permission(store, appointee, permission)
    
    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        return self.session.permissions_of(store, subject)
    
    def get_store_personal(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_store_personal(store_name)

    def get_store_purchase_history(self, store_name: str) -> Response[dict]:
        return self.session.get_store_purchase_history(store_name)

    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        return self.session.start_auction(store_name, product_name, initial_price, duration)
    
    def start_lottery(self, store_name: str, product_name: str) -> Response:
        return self.session.start_lottery(store_name, product_name)

    def start_bid(self, store_name: str, product_name: str) -> Response:
        return self.session.start_bid(store_name, product_name)
    
    def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response:
        return self.session.approve_bid(store_name, product_name, is_approve)
    
    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        return self.session.add_purchase_simple_rule(store_name, product_name, gle, amount)
    
    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str,
                                  amount2: int, complex_rule_type: str) -> Response:
        return self.session.add_purchase_complex_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2, complex_rule_type)

    #######################
    # user search services
    def get_all_stores(self) -> Response[list[dict] | bool]:
        return self.session.get_all_stores()
    
    def get_store(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_store(store_name)
    
    def get_store_products(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_all_products_of(store_name)
    
    def get_products_by_name(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_name(name)
    
    def get_products_by_category(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_category(name)
    
    def get_products_by_keywords(self, keywords: list[str]) -> \
            Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_keywords(keywords)

    def get_products_in_price_range(self, _min: float, _max: float) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_in_price_range(_min, _max)
    
    # def filter_products_by_rating(self, low: int, high: int) -> Response[dict]:
    #     ...
    #
    #
    # def filter_products_by_category(self, category: str) -> Response[dict]:
    #     ...
    #
    #
    # def filter_products_by_store_rating(self, low: int, high: int) -> Response[dict]:
    #     ...

    ###################
    # admin service
    def cancel_membership_of(self, member_name: str) -> Response[bool]:
        return self.session.cancel_membership_of(member_name)

    def shutdown(self) -> Response[bool]:
        return self.session.shutdown()

