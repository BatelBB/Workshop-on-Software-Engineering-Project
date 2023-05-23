from idlelib.multicall import r
from typing import Optional, List, Dict, Any

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

    def get_permissions(self, username, store_name):
        return self._session.permissions_of(username, store_name)

