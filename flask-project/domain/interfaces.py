from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any

from domain.resource_manager import IResourceManager


class IExternalDeliveryService(ABC):
    ...


class IProduct(ABC):
    id: int
    name: str
    price: float



class IExternalPaymentService(ABC):
    @abstractmethod
    def pay(self, buyer, seller, amount) -> bool:
        ...


class IShop(ABC):
    def payment(self):
        ...

    def search_products(self):
        ...

    def add_item(self):
        ...

    def update_quantity(self, item, amount):
        ...

    def add_payment_service(self):
        ...

    def delete_payment_service(self):
        ...


class IRegisteredUser(ABC):
    username: str
    password: object  # TODO


class UserSession(ABC):
    _registered_user: Optional[IRegisteredUser]

    def login(self, username, password):
        ...

    def register(self):
        ...

    def logout(self):
        ...

    def purchase_cart(self):
        ...

    def create_store(self):
        ...

    def appoint_manager(self, shop, manager):
        ...

    def fire_manager(self, shop, manager):
        ...

    def appoint_owner(self, shop, manager):
        ...

    def fire_owner(self, shop, manager):
        ...

    # TODO req 4.7

    def close_store(self):
        ...

    def get_shop_personnel(self, shop_id):
        ...

    def get_purchase_history_for_shop(self, shop_id):
        ...


class IMarket(ABC):
    delivery_services: IResourceManager[IExternalDeliveryService]
    payment_services: IResourceManager[IExternalPaymentService]
    registered_users: IResourceManager[IRegisteredUser]
    _sessions: List[UserSession]

    def startup(self):
        ...

    def boot(self):
        ...

    def payment(self):
        ...

    def create_delivery(self):
        ...

    def start_session(self) -> UserSession:
        ...

    def end_session(self, session: UserSession):
        ...

    def search_shop(self, shop_id) -> IShop:
        ...

    def get_shop_list(self):
        ...

    def get_shop_products(self, shop_id):
        ...

    def search_product(self):
        ...

