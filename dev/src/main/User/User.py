from dev.src.main.Service.IService import IService
from dev.src.main.User.Cart import Cart
from dev.src.main.Utils.Response import Response
from dev.src.main.Store.Product import Product
from dev.src.main.User.Role.Visitor import Visitor


class User:
    def __init__(self, mediator: IService, username: str = "Visitor", encrypted_password: str = "Visitor"):
        self.mediator = mediator
        self.username = username
        self.encrypted_password = encrypted_password
        self.role = Visitor(self)
        self.founded_stores: list[str] = list()
        # we map store_name to all appointees (username) which were appointed by self (might be StoreOwner or StoreManager)
        self.appointees: dict[str, list[str]] = dict()
        self.cart = Cart()
        self.owned_stores: list[str] = list()

    def __str__(self):
        return self.role.__str__()

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def leave(self, session_identifier: int):
        self.role.leave(session_identifier)

    def register(self) -> Response[bool]:
        return self.role.register()

    def login(self, encrypted_password: str) -> Response[bool]:
        return self.role.login(encrypted_password)

    def logout(self) -> Response[bool]:
        return self.role.logout()

    def is_logged_in(self) -> bool:
        return self.role.is_logged_in()

    def open_store(self, store_name: str) -> Response[bool]:
        return self.role.open_store(store_name)

    def close_store(self, store_name: str) -> Response[bool]:
        return self.role.close_store(store_name)

    def add_product(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        return self.role.add_product(store_name, product, quantity)

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.role.update_product_quantity(store_name, product_name, quantity)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.role.remove_product(store_name, product_name)

    def add_to_cart(self, store_name: str, product_name: str, price: float, quantity: int = 1) -> Response[bool]:
        return self.role.add_to_cart(store_name, product_name, price, quantity)

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        return self.role.remove_product_from_cart(store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.role.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> Response[str]:
        return self.role.show_cart()

    def verify_cart_not_empty(self) -> Response[bool]:
        return self.role.verify_cart_not_empty()

    def get_baskets(self) -> dict:
        return self.role.get_baskets()

    def empty_basket(self, store_name: str):
        self.role.empty_basket(store_name)

    def is_allowed_to_appoint_owner(self, store_name: str, new_name: str) -> Response[bool]:
        return self.role.is_allowed_to_appoint_owner(store_name, new_name)

    def is_allowed_to_appoint_manager(self, store_name: str, new_name: str) -> Response[bool]:
        return self.role.is_allowed_to_appoint_manager(store_name, new_name)

    def make_me_owner(self, store_name: str) -> Response[bool]:
        return self.role.make_me_owner(store_name)

    def make_me_manager(self, store_name: str) -> Response[bool]:
        return self.role.make_me_manager(store_name)

    def change_product_name(self, store_name: str, product_name: str) -> Response[bool]:
        return self.role.change_product_name(store_name, product_name)

    def change_product_price(self, store_name: str, product_price: float) -> Response[bool]:
        return self.role.change_product_price(store_name, product_price)

    def is_allowed_to_get_store_purchase_history(self) -> Response[bool]:
        return self.role.is_allowed_to_get_store_purchase_history()

    def is_allowed_to_shutdown_market(self) -> Response[bool]:
        return self.role.is_allowed_to_shutdown_market()

