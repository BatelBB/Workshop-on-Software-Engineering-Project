from domain.main.Market.Permissions import Permission, get_permission_name, get_permission_description
from src.domain.main.Utils.Response import Response
from Service.bridge.Bridge import Bridge
from Service.bridge.real import Real


class Proxy(Bridge):
    real: Bridge

    def __init__(self):
        self.real = Real()

    ###################
    # general services
    def enter_market(self):
        self.real.enter_market()

    def exit_market(self) -> Response[bool]:
        return self.real.exit_market()

    def clear_data(self) -> None:
        self.real.clear_data()

    def register(self, username: str, password: str) -> Response[bool]:
        return self.real.register(username, password)

    def login(self, username: str, password: str) -> Response[bool]:
        return self.real.login(username, password)

    def logout(self) -> Response[bool]:
        return self.real.logout()

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

    def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str,
                               city: str, country: str) -> Response[bool]:
        return self.real.purchase_shopping_cart(payment_method, payment_details, address, postal_code, city, country)

    def purchase_with_non_immediate_policy(self, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str) -> Response[bool]:
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
        return Response(False)

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

    def change_product_price(self, store_name: str,
                             product_price: float, new_price: float) -> Response[bool]:
        return self.real.change_product_price(store_name, product_price, new_price)

    def appoint_owner(self, appointee: str, store: str) -> Response[bool]:
        return self.real.appoint_owner(appointee, store)

    def appoint_manager(self, appointee: str, store: str) -> Response[bool]:
        return self.real.appoint_manager(appointee, store)

    def appointees_at(self, store: str) -> Response[list[str] | bool]:
        return self.real.appointees_at(store)

    def remove_appointment(self, fired_appointee: str, store_name: str) -> Response[bool]:
        return self.real.remove_appointment(fired_appointee, store_name)

    def add_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.real.add_permission(store, appointee, permission.name)

    def remove_permission(self, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.real.remove_permission(store, appointee, permission)

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

    def get_store_purchase_history(self, store_name: str) -> Response[dict]:
        return self.real.get_store_purchase_history(store_name)

    def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool]:
        return self.real.start_auction(store_name, product_name, initial_price, duration)

    def start_lottery(self, store_name: str, product_name: str) -> Response:
        return self.real.start_lottery(store_name, product_name)

    def start_bid(self, store_name: str, product_name: str) -> Response:
        return self.real.start_bid(store_name, product_name)

    def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response:
        return self.real.approve_bid(store_name, product_name, is_approve)

    def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response:
        return self.real.add_purchase_simple_rule(store_name, product_name, gle, amount)

    def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str,
                                  gle2: str,
                                  amount2: int, complex_rule_type: str) -> Response:
        return self.real.add_purchase_complex_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2,
                                                   complex_rule_type)

    #######################
    # user search services
    def get_all_stores(self) -> Response[dict | bool]:
        res = self.real.get_all_stores()
        if not res.success:
            return res
        else:
            dic = {}
            for store in res.result:
                products = {}
                for product in store.products:
                    products[product.name] = {"Price": product.price, "Keywords": product.keywords,
                                              "Category": product.category, "Rate": product.rate,
                                              "Quantity": store.products_quantities[product.name].quantity}
                dic[store.name] = products
            return Response(dic)

    def get_store(self, store_name: str) -> Response[dict | bool]:
        return self.real.get_store(store_name)

    def get_store_products(self, store_name: str) -> Response[dict | bool]:
        res = self.real.get_store_products(store_name)
        if not res.success:
            return res
        else:
            products = {}
            for product in res.result:
                products[product.name] = {"Price": product.price, "Keywords": product.keywords,
                                          "Category": product.category, "Rate": product.rate}
            return Response(products)

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
        return self.real.cancel_membership_of(member_name)

    def shutdown(self) -> Response[bool]:
        return self.real.shutdown()
