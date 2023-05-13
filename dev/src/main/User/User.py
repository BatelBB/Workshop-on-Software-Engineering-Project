from dev.src.main.Service.IService import IService
from dev.src.main.Store.Product import Product
from dev.src.main.User.Cart import Cart
from dev.src.main.User.Role.Visitor import Visitor
from dev.src.main.Utils.Response import Response


class User:
    def __init__(self, mediator: IService, username: str = "Visitor", encrypted_password: str = "Visitor"):
        self.mediator = mediator
        self.username = username
        self.encrypted_password = encrypted_password
        self.is_canceled = False
        self.role = Visitor(self)
        self.cart = Cart()

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

    def is_member(self) -> bool:
        return self.role.is_member()

    def is_admin(self) -> bool:
        return self.role.is_admin()

    def add_to_cart(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        return self.role.add_to_cart(store_name, product, quantity)

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        return self.role.remove_product_from_cart(store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.role.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> str:
        return self.role.show_cart()