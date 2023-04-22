from abc import ABC

from dev.src.main.Store.Product import Product
from dev.src.main.Store.Store import Store
from dev.src.main.User.Role.Visitor import Visitor
from dev.src.main.Utils.Logger import report, report_error, report_info
from dev.src.main.Utils.Response import Response


class Member(Visitor, ABC):
    from dev.src.main.User.User import User
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'Member {self.context.username}'

    def login(self, encrypted_password: str):
        return report_error(self.login.__qualname__, f'{self} is already logged in.')

    def register(self) -> Response[bool]:
        return report_error(self.register.__qualname__, f'{self} is already registered.')

    def logout(self) -> Response[bool]:
        response = report_info(self.logout.__qualname__, f'{self} is logged out')
        self.context.role = Visitor(self.context)
        return response

    def is_logged_in(self) -> bool:
        return True

    def open_store(self, store_name: str) -> Response[bool]:
        from dev.src.main.User.Role.StoreOwner import StoreOwner
        self.context.role = StoreOwner(self.context, store_name)
        return report_info(self.open_store.__qualname__, f'{self} opens Store \'{store_name}\' successfully')

    def close_store(self, store_name: str) -> Response[bool]:
        self.context.appointees.pop(store_name)
        self.context.founded_stores.remove(store_name)
        return report_info(self.close_store.__qualname__, f'{self} closes Store \'{store_name}\' successfully')

    def is_appointed_of(self, store_name: str) -> Response[bool]:
        return Response(True) if store_name in (self.context.appointees or self.context.founded_stores)\
            else report_error(self.is_appointed_of.__qualname__, f'{self} is not authorized appointed of Store \'{store_name}\'!')

    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        return self.is_appointed_of(store_name)

    def add_product(self, store_name: str, product: Product, quantity: int) -> Response[bool]:
        return self.is_allowed_add_product(store_name)

    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        return self.is_appointed_of(store_name)

    def update_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return  self.is_allowed_update_product(store_name)

    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        return self.is_appointed_of(store_name)

    def remove_product(self, store_name: str, product_name: str) -> Response[bool]:
        return self.is_allowed_remove_product(store_name)

    def change_product_name(self, store_name: str, product_name: str) -> Response[bool]:
        return self.is_allowed_update_product(store_name)

    def change_product_price(self, store_name: str, product_price: float) -> Response[bool]:
        return self.is_allowed_update_product(store_name)