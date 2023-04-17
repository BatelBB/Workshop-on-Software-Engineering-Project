from abc import ABC

from dev.src.main.Store.Store import Store
from dev.src.main.User.Role.IRole import IRole
from dev.src.main.Utils.Logger import report, report_error, report_info
from dev.src.main.Utils.Response import Response


class Visitor(IRole, ABC):
    def __init__(self, context):
        super().__init__(context)

    def __str__(self):
        return f'Visitor(Guest)'

    def leave(self, session_identifier: int):
        self.context.mediator.close_session(session_identifier)
        return report_info(self.leave.__qualname__, f'{self} left session {session_identifier}!')

    def register(self) -> Response[bool]:
        return report_info(self.register.__qualname__, f'{self.context.username} is registered!')

    def login(self, encrypted_password: str):
        if encrypted_password != self.context.encrypted_password:
            return report_error(self.login.__qualname__, f'{self} enter an incorrect password.')
        from dev.src.main.User.Role.Member import Member
        self.context.role = Member(self.context)
        return report_info(self.login.__qualname__, f'{self.context.username} is logged in.')

    def logout(self) -> Response[bool]:
        return report_error(self.logout.__qualname__, f'{self} attempted to logout.')

    def is_logged_in(self) -> bool:
        return False

    def open_store(self, store_name: str) -> Response[bool]:
        return report_error(self.open_store.__qualname__, f'{self} attempted to open a store.')

    from dev.src.main.Store.Product import Product

    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        return report_error(self.is_allowed_add_product.__qualname__, f'{self} is not allowed to add a product!')

    def add_product(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        return self.is_allowed_add_product(store_name)

    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        return report_error(self.is_allowed_update_product.__qualname__, f'{self} is not allowed to update a product!')

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.is_allowed_update_product(store_name)

    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        return report_error(self.is_allowed_remove_product.__qualname__, f'{self} is not allowed to remove a product!')

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.is_allowed_remove_product(store_name)

    def add_to_cart(self, store_name: str, product_name: str, price: float, quantity: int) -> Response[bool]:
        self.context.cart.add_item(store_name, product_name, price, quantity)
        return report_info(self.add_to_cart.__qualname__, f'{quantity} units of Product \'{product_name}\' is added to {self}\' cart')

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        self.context.cart.remove_item(store_name, product_name)
        return report_info(self.remove_product_from_cart.__qualname__, f'Product \'{product_name}\' is removed from {self}\'s cart')

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        new_quantity = self.context.cart.update_item_quantity(store_name, product_name, quantity)
        return report_info(self.update_cart_product_quantity.__qualname__,
                           f'Product \'{product_name}\', of {self} cart is set to {new_quantity}.')

    def show_cart(self) -> Response[bool]:
        return report_info(self.show_cart.__qualname__, self.context.cart.__str__())