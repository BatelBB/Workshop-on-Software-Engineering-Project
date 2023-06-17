from domain.main.Market.Permissions import Permission
from src.domain.main.StoreModule.PurchaseRules.BasketRule import BasketRule
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.AndRule import AndRule
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.ConditioningRule import ConditioningRule
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.OrRule import OrRule
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.Utils.Response import Response
from Service.bridge.Bridge import Bridge
from Service.bridge.real import Real


class Proxy(Bridge):
    real: Real

    def __init__(self):
        self.real = Real()
        self.system_admin = ('Kfir', 'Kfir')
        self.provision_path = 'src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter' \
                              '.provisionService.getDelivery'
        self.payment_pay_path = 'src.domain.main.ExternalServices.Payment.PaymentServices.PaymentService.pay'
        self.payment_refund_path = 'src.domain.main.ExternalServices.Payment.PaymentServices.PaymentService.refund'

    ###################
    # general services
    def enter_market(self):
        self.real.enter_market()

    def exit_market(self) -> Response[bool]:
        return self.real.exit_market()

    def register(self, username: str, password: str) -> Response[bool]:
        return self.real.register(username, password)

    def login(self, username: str, password: str) -> Response[bool]:
        return self.real.login(username, password)

    def logout(self) -> Response[bool]:
        return self.real.logout()

    def send_message(self, recipient, content) -> Response[bool]:
        return self.real.send_message(recipient, content)

    def get_inbox(self) -> Response[dict | bool]:
        r = self.real.get_inbox()
        if not r.success:
            return Response(False)
        dic = {}
        notifications = r.result
        for n in notifications:
            dic[n.msg_id] = {"Sender": n.sender, "Recipient": n.recipient, "Seen": n.seen, "Sender_type": n.sender_type,
                             "Content": n.content, "Timestamp": n.timestamp}
        return Response(dic)

    def mark_read(self, msg_id: int) -> Response[bool]:
        return self.real.mark_read(msg_id)

    #########################
    # user purchase services
    def add_to_cart(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.real.add_to_cart(store_name, product_name, quantity)

    def remove_from_cart(self, store_name: str,
                         product_name: str) -> Response[bool]:
        return self.real.remove_from_cart(store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.real.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> Response[dict | bool]:
        return self.real.show_cart()

    def get_cart_price(self) -> Response[float]:
        cart = self.real.get_cart().result
        return self.real.get_cart_price(cart.baskets)

    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str,
                               city: str, country: str) -> Response[bool]:
        return self.real.purchase_shopping_cart(payment_method, payment_details, address, postal_code, city, country)

    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str, payment_method: str,
                                           payment_details: list[str], address: str, postal_code: str, how_much: float,
                                           city: str, country: str) -> Response[bool]:
        return self.real.purchase_with_non_immediate_policy(store_name, product_name, payment_method,
                                                            payment_details, address, postal_code, how_much, city,
                                                            country)

    ##############################
    # store management services
    def open_store(self, store_name: str) -> Response[bool]:
        return self.real.open_store(store_name)

    def close_store(self, store_name: str) -> Response[bool]:
        return self.real.close_store(store_name)

    def reopen_store(self, store_name: str) -> Response[bool]:
        return self.real.reopen_store(store_name)

    def remove_store(self, store_name: str) -> Response[bool]:
        return self.real.remove_store(store_name)

    def add_product(self, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str] = None) -> Response[bool]:
        return self.real.add_product(store_name, product_name, category, price, quantity, keywords)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.real.remove_product(store_name, product_name)

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.real.update_product_quantity(store_name, product_name, quantity)

    def change_product_name(self, store_name: str,
                            product_name: str, new_name: str) -> Response[bool]:
        return self.real.change_product_name(store_name, product_name, new_name)

    def change_product_price(self, store_name: str, product_price: float, new_price: float) -> Response[bool]:
        return self.real.change_product_price(store_name, product_price, new_price)

    def change_product_category(self, store_name: str, old_product_name: str, category: str) -> Response[bool]:
        return self.real.change_product_category(store_name, old_product_name, category)

    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        return self.real.appoint_owner(appointee, store)

    def approve_owner(self, appointee: str, store: str, is_approve: bool = True) -> Response[bool]:
        return self.real.approve_owner(appointee, store, is_approve)

    def appoint_manager(self, appointee: str, store: str) -> Response[bool]:
        return self.real.appoint_manager(appointee, store)

    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        return self.real.appointees_at(store)

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        return self.real.remove_appointment(fired_appointee, store_name)

    def add_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.real.add_permission(store, appointee, permission.name)

    def remove_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.real.remove_permission(store, appointee, permission.name)

    def permissions_of(self, store: str, subject: str) -> Response[set[Permission] | bool]:
        return self.real.permissions_of(store, subject)

    def get_store_staff(self, store_name: str) -> Response[dict | bool]:
        result = self.real.get_store_staff(store_name)
        if result.success:
            dic = {}
            for appointment in result.result:
                dic[appointment.appointee] = {"Appointed by": appointment.appointed_by,
                                              "Permissions": {p.value for p in appointment.permissions}}
            return Response(dic)
        else:
            return Response(False)

    def get_store_purchase_history(self, store_name: str):
        result = self.real.get_store_purchase_history(store_name)
        if isinstance(result, list):
            return Response(result[0])
        return result

    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        return self.real.start_auction(store_name, product_name, initial_price, duration)

    def start_lottery(self, store_name: str, product_name: str) -> Response:
        return self.real.start_lottery(store_name, product_name)

    def start_bid(self, store_name: str, product_name: str) -> Response:
        return self.real.start_bid(store_name, product_name)

    def approve_bid(self, store_name: str, product_name: str, is_approve: bool = True) -> Response[bool]:
        return self.real.approve_bid(store_name, product_name, is_approve)

    def get_store_approval_lists_and_bids(self, store_name) -> Response:
        r = self.real.get_store_approval_lists_and_bids(store_name)
        if isinstance(r, Response) and not r.success:
            return r
        elif isinstance(r, dict):
            dic = {"Owners": r['owners'], "Bids": r['bids']}
            return Response(dic)
        return r

    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        return self.real.add_purchase_simple_rule(store_name, product_name, gle, amount)

    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str,
                                  gle2: str,
                                  amount2: int, complex_rule_type: str) -> Response:
        return self.real.add_purchase_complex_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2,
                                                   complex_rule_type)

    def delete_purchase_rule(self, index, store_name) -> Response[bool]:
        return self.real.delete_purchase_rule(index, store_name)

    def add_basket_purchase_rule(self, store_name: str, min_price: float) -> Response[bool]:
        return self.real.add_basket_purchase_rule(store_name, min_price)

    def add_simple_discount(self, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None, rule_type=None, min_price: float = None, p1_name=None,
                            gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) -> Response[bool]:
        return self.real.add_simple_discount(store_name, discount_type, discount_percent, discount_for_name,
                                             rule_type, min_price, p1_name, gle1, amount1, p2_name, gle2, amount2)

    def connect_discounts(self, store_name, id1, id2, connection_type, rule_type=None, min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) \
            -> Response[bool]:
        return self.real.connect_discounts(store_name, id1, id2, connection_type, rule_type, min_price, p1_name,
                                           gle1, amount1, p2_name, gle2, amount2)

    def delete_discount(self, store_name: str, index: int) -> Response[bool]:
        return self.real.delete_discount(store_name, index)

    #######################
    # user search services
    def get_store(self, store_name: str) -> Response[dict | bool]:
        return self.real.get_store(store_name)

    def get_products_by_name(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        res = self.real.get_products_by_name(name)
        if not res.success:
            return res
        else:
            products = []
            for product in res.result:
                if not product.__eq__({}):
                    products.append(product)
            return Response(products)

    def get_products_by_category(self, name: str) -> Response[list[dict[str, dict]] | bool]:
        res = self.real.get_products_by_category(name)
        if not res.success:
            return res
        else:
            products = []
            for product in res.result:
                if not product.__eq__({}):
                    products.append(product)
            return Response(products)

    def get_products_by_keywords(self, keywords: list[str]) -> \
            Response[list[dict[str, dict]] | bool]:
        res = self.real.get_products_by_keywords(keywords)
        if not res.success:
            return res
        else:
            products = []
            for product in res.result:
                if not product.__eq__({}):
                    products.append(product)
            return Response(products)

    def get_products_in_price_range(self, _min: float, _max: float) -> Response[list[dict[str, dict]] | bool]:
        res = self.real.get_products_in_price_range(_min, _max)
        if not res.success:
            return res
        else:
            products = []
            for product in res.result:
                if not product.__eq__({}):
                    products.append(product)
            return Response(products)

    def get_discounts(self, store_name: str) -> Response[list[dict[int:str]]]:
        return self.real.get_discounts(store_name)

    def get_purchase_rules(self, store_name: str) -> Response[dict[int:dict]]:
        r = self.real.get_purchase_rules(store_name)
        if not r.success:
            return r
        dic = {}
        for rule in r.result.values():
            if isinstance(rule, SimpleRule):
                dic[rule.rule_id] = {"Type": "simple", "Product": rule.product_name, "Gle": rule.gle, "Amount": rule.num}
            elif isinstance(rule, BasketRule):
                dic[rule.rule_id] = {"Type": "basket", "Min price": rule.min_price}
            elif isinstance(rule, OrRule):
                dic[rule.rule_id] = {"Type": "or", "Rule1 id": rule.rule_id1, "Rule2 id": rule.rule_id2}
            elif isinstance(rule, AndRule):
                dic[rule.rule_id] = {"Type": "and", "Rule1 id": rule.rule_id1, "Rule2 id": rule.rule_id2}
            elif isinstance(rule, ConditioningRule):
                dic[rule.rule_id] = {"Type": "conditional", "Rule1 id": rule.rule_id1, "Rule2 id": rule.rule_id2}
            else:
                raise NotImplemented
        return Response(dic)

    def get_bid_products(self, store_name: str) -> Response[dict | bool]:
        return self.real.get_bid_products(store_name)

    ###################
    # admin service
    def cancel_membership_of(self, member_name: str) -> Response[bool]:
        return self.real.cancel_membership_of(member_name)

    def shutdown(self) -> Response[bool]:
        self.real.login(*self.system_admin)
        return self.real.shutdown()

    def load_configuration(self) -> None:
        self.real.login(*self.system_admin)
        self.real.load_configuration()
        self.real.logout()

    # clear db data and call init market (need to load configuration)
    def clear_data(self) -> None:
        self.real.clear_data()
