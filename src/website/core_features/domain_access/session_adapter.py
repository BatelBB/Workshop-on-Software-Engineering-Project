import threading
from typing import Optional, List, Dict, Any, Set
from idlelib.multicall import r
from typing import Optional, List, Dict, Any, Set, Mapping

from src.domain.main.Market.Permissions import Permission
from src.domain.main.StoreModule.Store import Store
from src.domain.main.Utils.Response import Response
from Service.Session.Session import Session
from website.core_features.domain_access.session_adapter_dto import ProductDto, BasketDto


class SessionAdapter:
    def __init__(self, domain_session: Session):
        self._session = domain_session
        self._username: Optional[str] = None
        self._is_logged_in = False
        self.lock = threading.RLock()

    @property
    def is_logged_in(self):
        return self._is_logged_in

    @property
    def username(self):
        return self._username

    def get_stores(self) -> Response[List[Store]]:
        stores = self._session.get_all_stores()
        return stores

    def get_store(self, name) -> Response[List[ProductDto]]:
        response = self._session.get_store(name)
        if not response.success:
            return response
        data: Dict[str, Dict[str, Any]] = response.result
        products: List[ProductDto] = [
            ProductDto(
                name=product["Name"],
                category=product["Category"],
                quantity=product["Quantity"],
                rate=product["Rate"],
                price=product["Price"],
                store_name=name
            )
            for product in data.values()
        ]
        return Response(products)

    def register(self, username: str, password: str) -> Response[bool]:
        response = self._session.register(username, password)
        return response

    def login(self, username: str, password: str) -> Response[bool]:
        response = self._session.login(username, password)
        if response.success and response.result:
            self._username = username
            self._is_logged_in = True
        return response

    def logout(self):
        response = self._session.logout()
        if response.success and response.result:
            self._username = None
            self._is_logged_in = False
        return response

    def open_store(self, store_name: str):
        return self._session.open_store(store_name)

    def remove_store(self, store_name: str):
        return self._session.remove_store(store_name)

    def get_deleted_stores(self):
        return self._session.get_all_deleted_stores()

    def your_stores(self):
        response = self.get_stores()
        if not response.success:
            return response
        return Response([store for store in response.result if self.has_a_role_at(store.name).result])

    def has_a_role_at(self, store_name: str) -> Response[bool]:
        perm = self._session.permissions_of(store_name, self._username)
        if not perm.success:
            return Response(False)
        return Response(len(perm.result) > 0)

    def permissions_of(self, store_name: str) -> Set[Permission]:
        if not self.is_logged_in:
            return set()
        res = self._session.permissions_of(store_name, self.username)
        return res.result if res.success else set()

    def get_admin_permissions(self) -> Set[Permission]:
        if not self.is_logged_in:
            return set()
        res = self._session.get_admin_permissions()
        return res.result if res.success else set()

    def add_product(self, store_name: str, product_name: str, category: str, price: float, quantity: int):
        return self._session.add_product(store_name, product_name, category, price, quantity)

    def edit_product(self, store_name, old_product_name, new_product_name, category, price, qty):
        r = self._session.change_product_price(store_name, old_product_name, price)
        if not r.success:
            return r
        r = self._session.update_product_quantity(store_name, old_product_name, qty)
        if not r.success and store_name != old_product_name:
            r = self._session.change_product_name(store_name, old_product_name, new_product_name)
        return r

    def get_basket(self, store_name: str) -> Response[BasketDto]:
        r_cart = self._session.get_cart()
        if not r_cart.success:
            return r_cart
        cart = r_cart.result
        if not cart.has_basket(store_name):
            return Response(BasketDto(store_name, dict(), dict()))
        basket = cart.get_or_create_basket(store_name)
        return Response(BasketDto(store_name=store_name,
                                  amounts={
                                      x.product_name: x.quantity
                                      for x in basket.items
                                  },
                                  products={
                                      x.product_name: x
                                      for x in basket.items
                                  }
                                  ))

    def get_product(self, store_name, product_name) -> Response[ProductDto]:
        store = self.get_store(store_name)
        if not store.success:
            return store
        return next(
            (Response(product)
             for product in store.result
             if product.name == product_name),
            Response("no such product")  # \← default if not found
        )

    def update_cart_product_quantity(self, store_name, product_name, qty) -> Response[None]:
        return self._session.update_cart_product_quantity(store_name, product_name, qty)

    def edit_product_name(self, store_name: str, old_product_name: str, new_product_name: str):
        return self._session.change_product_name(store_name, old_product_name, new_product_name)

    def edit_product_category(self, store_name: str, old_product_name: str, category: str):
        return self._session.change_product_category(store_name, old_product_name, category)

    def edit_product_price(self, store_name: str, old_product_price: float, price: float):
        return self._session.change_product_price(store_name, old_product_price, price)

    def edit_product_quantity(self, store_name: str, old_product_name: str, quantity: int):
        return self._session.update_product_quantity(store_name, old_product_name, quantity)

    def appoint_manager(self, store_name: str, appointee: str):
        return self._session.appoint_manager(appointee, store_name)

    def appoint_owner(self, store_name: str, appointee: str):
        return self._session.appoint_owner(appointee, store_name)

    def remove_manager(self, store_name: str, name: str):
        return self._session.remove_appointment(name, store_name)

    def remove_owner(self, store_name: str, name: str):
        return self._session.remove_appointment(name, store_name)

    def get_all_registered_users(self):
        return self._session.get_all_registered_users()

    def remove_product(self, store_name: str, product_name: str):
        return self._session.remove_product(store_name, product_name)

    def get_purchase_rules(self, store_name: str) -> list[str]:
        rules = self._session.get_purchase_rules(store_name)
        if not rules.success:
            return None
        rules_dict: dict = rules.result
        rule_str_dict = {}
        for rule_num in rules_dict.keys():
            rule_str_dict[rule_num] = rules_dict[rule_num].__str__()

        return rule_str_dict

    def delete_purchase_rule(self, index: int, store_name: str):
        self._session.delete_purchase_rule(index, store_name)

    def add_simple_purchase_rule(self, store_name: str, p_name, gle, amount):
        res = self._session.add_purchase_simple_rule(store_name, p_name, gle, amount)
        if res.success:
            return 'successfuly added rule'
        return res.description

    def add_complex_purchase_rule(self, store_name, p1_name, gle1, amount1, p2_name, gle2, amount2, rule_type):
        res = self._session.add_purchase_complex_rule(store_name, p1_name, gle1, amount1, p2_name, gle2, amount2,
                                                      rule_type)
        if res.success:
            return 'successfuly added rule'
        return res.description

    def add_basket_purchase_rule(self, store_name, min_price):
        res = self._session.add_basket_purchase_rule(store_name, min_price)
        if res.success:
            return 'successfuly added rule'
        return res.description

    def get_discounts(self, store_name):
        res = self._session.get_discounts(store_name)
        if not res.success:
            return None
        l = res.result
        d = l[0]
        d.update(l[1])
        return d

    def delete_discount(self, store_name, index):
        res = self._session.delete_discount(store_name, index)
        return res.description

    def add_simple_discount(self, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None,
                            rule_type=None, min_price: float = None,
                            p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        res = self._session.add_simple_discount(store_name, discount_type, discount_percent,
                                                discount_for_name,
                                                rule_type, min_price,
                                                p1_name, gle1, amount1, p2_name, gle2, amount2)
        return res.description

    def connect_discounts(self, store_name: str, id1: int, id2: int, connection_type: str,
                          rule_type=None, min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        res = self._session.connect_discounts(store_name, id1, id2, connection_type,
                                              rule_type, min_price,
                                              p1_name, gle1, amount1, p2_name, gle2, amount2)
        return res.description

    def get_cart(self) -> Response[Mapping[str, BasketDto]]:
        cart = self._session.get_cart()
        if not cart.success:
            return cart
        return Response({
            store_name: self.get_basket(store_name).result
            for store_name in cart.result.baskets.keys()
        })

    def get_cart_price(self):
        cart = self._session.get_cart()
        if not cart.success:
            return cart
        return self._session.get_cart_price(cart.result.baskets)

    def purchase_by_card(self, number, exp_month, exp_year, ccv, street, apt_number, city, country):
        return self._session.purchase_shopping_cart('card', [str(number), f'{exp_month}/{exp_year}', ccv],
                                                    street, apt_number, city, country)

    def get_all_products(self):
        list_of_all_products = {}
        # for all stores
        store_response = self.get_stores()
        # for all products in stores
        for store in store_response.result:
            set_of_products = store.get_all()
            list_of_all_products[store.name] = set_of_products
            # return a list with all the products
        return list_of_all_products

    def get_all_store_owners(self, store_name: str):
        resp = self._session.get_store_owners(store_name)
        if resp.success:
            return resp.result
        return resp

    def get_all_store_managers(self, store_name: str):
       resp = self._session.get_store_managers(store_name)
       if resp.success:
           return resp.result
       return resp

    def get_purchase_history_owner(self, store_name: str):
        return self._session.get_store_purchase_history(store_name)

