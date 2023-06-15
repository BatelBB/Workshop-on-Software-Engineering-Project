from Service.IService.IService import IService
from Service.Session.Session import Session
from domain.main.Market.Permissions import Permission
from domain.main.Notifications.notification import Notification
from domain.main.StoreModule.PurchaseRules.IRule import IRule
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
    def enter_market(self) -> None:
        self.session = self.market.enter()

    def exit_market(self) -> Response[bool]:
        return self.session.leave()

    def register(self, username: str, password: str) -> Response[bool]:
        return self.session.register(username, password)

    def login(self, username: str, password: str) -> Response[bool]:
        return self.session.login(username, password)

    def logout(self) -> Response[bool]:
        return self.session.logout()

    def send_message(self, recipient, content) -> Response[bool]:
        return self.session.send_message(recipient, content)

    def get_inbox(self) -> Response[list[Notification]]:
        return self.session.get_inbox()

    def mark_read(self, msg_id: int) -> Response[bool]:
        return self.session.mark_read(msg_id)

    #########################
    # user purchase services
    def add_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.session.add_to_cart(store_name, product_name, quantity)

    def remove_from_cart(self, store_name: str,
                         product_name: str) -> Response[bool]:
        return self.session.remove_product_from_cart(store_name, product_name)

    def add_product_quantity_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.session.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> Response[dict | bool]:
        return self.session.show_cart()

    def get_cart(self):
        return self.session.get_cart()

    def get_cart_price(self, basket):
        return self.session.get_cart_price(basket)

    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str,
                               city: str, country: str) -> Response[bool]:
        return self.session.purchase_shopping_cart(payment_method, payment_details, address, postal_code, city, country)

    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str, payment_method: str,
                                           payment_details: list[str], address: str, postal_code: str, how_much: float,
                                           city: str, country: str) -> Response[bool]:
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

    def change_product_name(self, store_name: str, product_name: str, new_name: str) -> Response[bool]:
        return self.session.change_product_name(store_name, product_name, new_name)

    def change_product_price(self, store_name: str, product_price: float, new_price: float) -> Response[bool]:
        return self.session.change_product_price(store_name, product_price, new_price)

    def change_product_category(self, store_name: str, old_product_name: str, category: str) -> Response[bool]:
        return self.session.change_product_category(store_name, old_product_name, category)

    # appointments and permissions
    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        return self.session.appoint_owner(appointee, store)

    def approve_owner(self, appointee: str, store: str, is_approve: bool) -> Response[bool]:
        return self.session.approve_owner(appointee, store, is_approve)

    def appoint_manager(self, appointee: str, store: str) -> Response[bool]:
        return self.session.appoint_manager(appointee, store)

    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        return self.session.appointees_at(store)

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        return self.session.remove_appointment(fired_appointee, store_name)

    def add_permission(self, store: str, appointee: str, permission) -> Response[bool]:
        return self.session.add_permission(store, appointee, permission)

    def remove_permission(self, store: str, appointee: str, permission) -> Response[bool]:
        return self.session.remove_permission(store, appointee, permission)

    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        return self.session.permissions_of(store, subject)

    def get_store_staff(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_store_staff(store_name)

    def get_store_purchase_history(self, store_name: str):
        return self.session.get_store_purchase_history(store_name)

    # product policies
    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        return self.session.start_auction(store_name, product_name, initial_price, duration)

    def start_lottery(self, store_name: str, product_name: str) -> Response[bool]:
        return self.session.start_lottery(store_name, product_name)

    def start_bid(self, store_name: str, product_name: str) -> Response[bool]:
        return self.session.start_bid(store_name, product_name)

    def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response[bool]:
        return self.session.approve_bid(store_name, product_name, is_approve)

    def get_store_approval_lists_and_bids(self, store_name) -> Response:
        return self.session.get_approval_lists_for_store(store_name)

    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response[bool]:
        return self.session.add_purchase_simple_rule(store_name, product_name, gle, amount)

    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str,
                                  amount2: int, complex_rule_type: str) -> Response[bool]:
        return self.session.add_purchase_complex_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2,
                                                      complex_rule_type)

    def delete_purchase_rule(self, index, store_name) -> Response[bool]:
        return self.session.delete_purchase_rule(index, store_name)

    def add_basket_purchase_rule(self, store_name: str, min_price: float) -> Response[bool]:
        return self.session.add_basket_purchase_rule(store_name, min_price)

    def add_simple_discount(self, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None, rule_type=None, min_price: float = None, p1_name=None,
                            gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) -> Response[bool]:
        return self.session.add_simple_discount(store_name, discount_type, discount_percent, discount_for_name,
                                                rule_type, min_price, p1_name, gle1, amount1, p2_name, gle2, amount2)

    def connect_discounts(self, store_name, id1, id2, connection_type, rule_type=None, min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) \
            -> Response[bool]:
        return self.session.connect_discounts(store_name, id1, id2, connection_type, rule_type, min_price,
                                              p1_name, gle1, amount1, p2_name, gle2, amount2)

    def delete_discount(self, store_name: str, index: int) -> Response[bool]:
        return self.session.delete_discount(store_name, index)

    #######################
    # user search services
    def get_store(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_store(store_name)

    def get_products_by_name(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_name(name)

    def get_products_by_category(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_category(name)

    def get_products_by_keywords(self, keywords: list[str]) -> \
            Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_by_keywords(keywords)

    def get_products_in_price_range(self, _min: float, _max: float) -> Response[list[dict[str, dict]] | bool]:
        return self.session.get_products_in_price_range(_min, _max)

    def get_discounts(self, store_name: str) -> Response[list[dict[int:str]]]:
        return self.session.get_discounts(store_name)

    def get_purchase_rules(self, store_name: str) -> Response[dict[int:IRule]]:
        return self.session.get_purchase_rules(store_name)

    def get_bid_products(self, store_name: str) -> Response[dict | bool]:
        return self.session.get_bid_products(store_name)

    ###################
    # admin service
    def cancel_membership_of(self, member_name: str) -> Response[bool]:
        return self.session.cancel_membership_of(member_name)

    def shutdown(self) -> Response[bool]:
        return self.session.shutdown()

    def clear_data(self) -> None:
        self.market.clear()

    def load_configuration(self) -> None:
        self.session.load_configuration()
