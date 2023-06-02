from idlelib.multicall import r
from typing import Optional, List, Dict, Any, Set

from domain.main.Market.Permissions import Permission
from domain.main.Store.Store import Store
from domain.main.Utils.Response import Response
from domain.main.Utils.Session import Session
from website.core_features.domain_access.session_adapter_dto import ProductDto


class SessionAdapter:
    def __init__(self, domain_session: Session):
        self._session = domain_session
        self._username: Optional[str] = None
        self._is_logged_in = False

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
                price=product["Price"]
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
