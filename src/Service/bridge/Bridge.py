from abc import ABC, abstractmethod
from src.domain.main.Market.Permissions import Permission
from src.domain.main.Utils.Response import Response


class Bridge(ABC):
    ###################
    # general services
    @abstractmethod
    def enter_market(self) -> None:
        ...

    @abstractmethod
    def exit_market(self) -> Response[bool]:
        ...

    @abstractmethod
    def clear_data(self) -> None:
        ...

    @abstractmethod
    def register(self, username: str, password: str) -> Response[bool]:
        ...

    @abstractmethod
    def login(self, username: str, password: str) -> Response[bool]:
        ...
    
    @abstractmethod
    def logout(self, ) -> Response[bool]:
        ...

    @abstractmethod
    def send_message(self, recipient, content):
        ...

    @abstractmethod
    def get_inbox(self):
        ...

    @abstractmethod
    def mark_read(self, msg_id: int):
        ...

    #########################
    # user purchase services 
    @abstractmethod
    def add_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def remove_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_product_quantity_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def show_cart(self) -> Response[dict | bool]:
        ...

    @abstractmethod
    def get_cart_price(self) -> Response[float]:
        ...

    @abstractmethod
    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str,
                               city: str, country: str) -> Response[bool]:
        ...

    @abstractmethod
    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str, payment_method: str,
                                           payment_details: list[str], address: str, postal_code: str, how_much: float,
                                           city: str, country: str) -> Response[bool]:
        ...

    ##############################
    # store management services
    @abstractmethod
    def open_store(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def close_store(self, store_name: str) -> Response[bool]:
        ...

    def reopen_store(self, store_name: str) -> Response[bool]:
        ...

    def remove_store(self, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_product(self, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str] = None) -> Response[bool]:
        ...

    @abstractmethod
    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_name(self, store_name: str,
                            product_name: str, new_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_price(self, store_name: str,
                             product_price: float, new_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def change_product_category(self, store_name, old_product_name, category) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        ...

    @abstractmethod
    def approve_owner(self, appointee: str, store: str, is_approve: bool) -> Response[bool]:
        ...

    @abstractmethod
    def appoint_manager(self, appointee: str, store: str) -> Response[bool]:
        ...

    @abstractmethod
    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        ...

    @abstractmethod
    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def add_permission(self, store: str, appointee: str, permission) -> Response[bool]:
        ...

    @abstractmethod
    def remove_permission(self, store: str, appointee: str, permission) -> Response[bool]:
        ...

    @abstractmethod
    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        ...

    @abstractmethod
    def get_store_staff(self, store_name: str) -> Response[dict | bool]:
        ...

    @abstractmethod
    def get_store_purchase_history(self, store_name: str):
        ...
    
    @abstractmethod
    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        ...

    @abstractmethod
    def start_lottery(self, store_name: str, product_name: str) -> Response:
        ...

    @abstractmethod
    def start_bid(self, store_name: str, product_name: str) -> Response:
        ...

    @abstractmethod
    def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response:
        ...

    @abstractmethod
    def get_approval_lists_for_store_bids(self, store_name) -> Response:
        ...

    @abstractmethod
    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        ...

    @abstractmethod
    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str, 
                                  amount2: int, complex_rule_type: str) -> Response:
        ...

    @abstractmethod
    def delete_purchase_rule(self, index, store_name) -> Response[bool]:
        ...

    @abstractmethod
    def add_basket_purchase_rule(self, store_name: str, min_price: float) -> Response[bool]:
        ...

    @abstractmethod
    def add_simple_discount(self, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None, rule_type=None, min_price: float = None, p1_name=None,
                            gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) -> Response[bool]:
        ...

    @abstractmethod
    def connect_discounts(self, store_name, id1, id2, connection_type, rule_type=None, min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) \
            -> Response[bool]:
        ...

    @abstractmethod
    def delete_discount(self, store_name: str, index: int) -> Response[bool]:
        ...
    
    #######################
    # user search services
    @abstractmethod
    def get_store(self, store_name: str) -> Response[dict | bool]:
        ...

    @abstractmethod
    def get_products_by_name(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_by_category(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_by_keywords(self, keywords: list[str]) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_products_in_price_range(self, _min: float, _max: float) -> Response[list[dict[str, dict]] | bool]:
        ...

    @abstractmethod
    def get_discounts(self, store_name: str) -> Response[list[dict[int:str]]]:
        ...

    @abstractmethod
    def get_purchase_rules(self, store_name: str):
        ...

    @abstractmethod
    def get_bid_products(self, store_name: str) -> Response[dict | bool]:
        ...

    ###################
    # admin service
    @abstractmethod
    def cancel_membership_of(self, member_name: str) -> Response[bool]:
        ...

    @abstractmethod
    def shutdown(self) -> Response[bool]:
        ...
