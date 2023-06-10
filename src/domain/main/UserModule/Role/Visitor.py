import threading
from abc import ABC

import bcrypt

from src.domain.main.Utils.Base_db import session_DB
from src.domain.main.Store.Store import Store
from src.domain.main.UserModule.Role.IRole import IRole
from src.domain.main.Utils.Logger import report_error, report_info
from src.domain.main.Utils.Response import Response


class Visitor(IRole, ABC):

    register_lock = threading.Lock()
    def __init__(self, context):
        super().__init__(context)

    def __str__(self):
        return f'Visitor'

    def register(self) -> Response[bool]:
        with Visitor.register_lock:
            if not self.context.is_registered(self.context.username):
                session_DB.merge(self.context)
                session_DB.commit()
                return report_info(self.register.__qualname__, f'\'{self.context.username}\' is registered!')
        return report_error(self.register.__qualname__, f'Username: \'{self.context.username}\' is occupied')

    def login(self, input_password: str) -> bool:
        is_password_matched = bcrypt.checkpw(bytes(input_password, 'utf8'), self.context.encrypted_password)
        if is_password_matched:
            from src.domain.main.UserModule.Role.Member import Member
            self.context.role = Member(self.context)
            self.context.is_logged_in = True
        return is_password_matched

    def logout(self) -> Response[bool]:
        return report_error(self.logout.__qualname__, f'{self} attempted to logout.')

    def is_logged_in(self) -> bool:
        return False

    def is_member(self) -> bool:
        return False

    def is_admin(self) -> bool:
        return False

    def add_manager_appointment(self, store: Store) -> Response[bool]:
        return report_error(self.add_manager_appointment.__qualname__, f'{self} is not allowed to be appointed as a StoreManagerr')

    def add_owner_appointment(self, store: Store) -> Response[bool]:
        return report_error(self.add_owner_appointment.__qualname__, f'{self} is not allowed to be appointed as a StoreOwner')

    def add_to_cart(self, store: str, product: str, price: float, quantity: int = 1) -> Response[bool]:
        self.context.cart.add_item(store, product, price, quantity)
        return report_info(self.add_to_cart.__qualname__, f'{quantity} units of Product \'{product}\' from store \'{store}\' is added to {self} cart')

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        self.context.cart.remove_item(store_name, product_name)
        return report_info(self.remove_product_from_cart.__qualname__, f'Product \'{product_name}\' is removed from {self} cart')

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        new_quantity = self.context.cart.update_item_quantity(store_name, product_name, quantity)
        return report_info(self.update_cart_product_quantity.__qualname__,f'Product \'{product_name}\', of {self} cart is set to {new_quantity}.')

    def show_cart(self) -> Response[dict]:
        return Response(self.context.cart.__dic__(), f'Cart of {self}:\n{self.context.cart.__str__()}')

    def verify_cart_not_empty(self) -> Response[bool]:
        return report_info(self.verify_cart_not_empty.__qualname__, f'{self} cart\'s is NOT empty!') if not self.context.cart.is_empty() \
            else report_error(self.verify_cart_not_empty.__qualname__, f'{self} cart\'s IS empty!')

    def get_baskets(self) -> dict:
        return self.context.cart.baskets

    def empty_basket(self, store_name: str) -> None:
        self.context.cart.empty_basket(store_name)
