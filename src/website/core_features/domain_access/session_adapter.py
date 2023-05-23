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

    def get_stores(self) -> List[Store]:
        stores = self._session.get_all_stores()
        return stores.get_or_throw()

    def get_store(self, name) -> List[ProductDto]:
        response = self._session.get_store(name)
        products: List[ProductDto] = [
            ProductDto(
                name=product["Name"],
                category=product["Category"],
                quantity=product["Quantity"],
                rate=product["Rate"],
                price=product["Price"]
            )
            for product in response.get_or_throw().values()
        ]
        return products

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
        stores = self.get_stores()
        return [store for store in stores if self.has_a_role_at(store.name)]

    def has_a_role_at(self, store_name: str) -> bool:
        return 0 < len(self.get_permissions(self._username, store_name))

    def get_permissions(self, username, store_name) -> Set[Permission]:
        return self._session.permissions_of(store_name, username).get_or(set())