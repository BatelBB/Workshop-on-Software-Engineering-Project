import random
import sys
from typing import Any

from dev.src.main.ExternalServices.Payment.PaymentFactory import PaymentFactory
from dev.src.main.Store.Product import Product
from dev.src.main.Service.IService import IService
from dev.src.main.Store.Store import Store
from dev.src.main.User.Basket import Basket
from dev.src.main.User.User import User
from dev.src.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from dev.src.main.Utils.Logger import report, Logger, report_error, report_info
from dev.src.main.Utils.Response import Response
from dev.src.main.Utils.Session import Session


# TODO: might be implemented as a Reactor: a singleton with a thread pool responsible for executing tasks
class Market(IService):

    # TODO: should be initialized with IPaymentService, IProvisionService
    def __init__(self):
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.payment_factory: PaymentFactory = PaymentFactory()

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.sessions.get(identifier) is None:
                return identifier

    def get_active_user(self, session_identifier: int) -> User | None:
        return self.sessions.get(session_identifier)

    def enter(self) -> Session:
        session_identifier = self.generate_session_identifier()
        self.sessions.insert(session_identifier, User(self))
        session = Session(session_identifier, self)
        Logger().post(f'{session} has been initialized')
        return session

    def close_session(self, session_identifier: int) -> None:
        self.sessions.delete(session_identifier)

    def shutdown(self) -> None:
        Logger().post('Market is closed!', Logger.Severity.WARNING)
        Logger().shutdown()

    def verify_registered_store(self, calling_method_name: str, store_name: str) -> Response[Store] | Response[bool]:
        store: Store = self.stores.get(store_name)
        return Response(store) if store is not None \
            else report_error(calling_method_name, f'Store \'{store_name}\' is not registered to the market.')

    def verify_store_contains_product(self, calling_method_name: str, store_name: str, product_name: str) -> \
            Response[Store] | Response[bool]:
        response = self.verify_registered_store(calling_method_name, store_name)
        if response.success:
            store = response.result
            if store.contains_product(product_name):
                return Response(store)
            else:
                return report_error(calling_method_name,
                                    f'Store \'{store_name}\' does not contains Product \'{product_name}\'')
        else:
            return response

    def leave(self, session_identifier: int) -> Response[bool]:
        leaving_user = self.sessions.delete(session_identifier)
        return leaving_user.leave(session_identifier)

    def register(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        new_user = User(self, username, encrypted_password)
        registered_user_with_param_username = self.users.insert(username, new_user)
        if registered_user_with_param_username is None:
            return new_user.register()
        else:
            return report_error(self.register.__qualname__, f'Username: \'{username}\' is occupied')

    def is_registered(self, username: str) -> bool:
        return self.users.get(username) is not None

    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        registered_user = self.users.get(username)
        if registered_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered)')
        else:
            response = registered_user.login(encrypted_password)
            if registered_user.is_logged_in():
                self.sessions.update(session_identifier, registered_user)
            return response

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in()

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        return actor.logout()

    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        store: Store = Store(store_name)
        registered_store_with_same_name = self.stores.insert(store_name, store)
        if registered_store_with_same_name is None:
            actor = self.get_active_user(session_identifier)
            response = actor.open_store(store_name)
            if not response.success:
                self.stores.delete(store_name)
            return response
        return report_error(self.open_store.__qualname__, f'Store name \'{store_name}\' is occupied.')

    def get_all_stores(self, session_identifier: int) -> Response[bool]:
        stores: str = self.stores.to_string_keys()
        there_are_stores: bool = len(stores) > 0
        preface: str = f'Displaying stores to {self.get_active_user(session_identifier)}: '
        no_stores_msg: str = 'Currently, there are no stores at the market.'
        return report(preface + stores if there_are_stores else preface + no_stores_msg, there_are_stores)

    def get_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        response = self.verify_registered_store(self.get_store.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_identifier)
            preface: str = f'Displaying store {response.result.name} to {actor}\n'
            return report_info(self.get_store.__qualname__, preface + response.result.__str__())
        else:
            return response

    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:

        actor = self.get_active_user(session_identifier)
        product = Product(product_name, category, price, keywords)
        response = actor.add_product(store_name, product, quantity)
        if response.success:
            response = self.verify_registered_store(self.add_product.__qualname__, store_name)
            store = response.result
            return store.add(product, quantity) if response.success else response
        else:
            return response

    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> \
            Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = actor.update_product_quantity(store_name, product_name, quantity)
        if response.success:
            response = self.verify_registered_store(self.update_product_quantity.__qualname__, store_name)
            store = response.result
            return store.update(product_name, quantity) if response.success else response
        else:
            return response

    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = actor.remove_product(store_name, product_name)
        if response.success:
            response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
            store = response.result
            return store.remove(product_name) if response.success else response
        else:
            return response

    def add_to_cart(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.add_to_cart.__qualname__, store_name, product_name)
        if response.success:
            store = response.result
            product_price = store.get_product_price(product_name)
            return actor.add_to_cart(store_name, product_name, product_price, quantity)
        else:
            return response

    def remove_product_from_cart(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.remove_product_from_cart.__qualname__, store_name,
                                                      product_name)
        return actor.remove_product_from_cart(store_name, product_name) if response.success else response

    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str,
                                     quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.update_cart_product_quantity.__qualname__, store_name,
                                                      product_name)
        return actor.update_cart_product_quantity(store_name, product_name, quantity) if response.success else response

    def show_cart(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        return actor.show_cart()

    def exit_market(self, session_identifier: int) -> Response[bool]:
        self.sessions.delete(session_identifier)
        return report_info("exit", "no error")

    def update_user_cart_after_purchase(self, user: User, store_names: list) -> Response[bool]:
        for store_name in store_names:
            user.empty_basket(store_name)

    # def update_store_product_quantity_after_purchase(self, store: Store, p_name: str, quantity: int):

    def pay(self, price: int, payment_type: str, payment_details: list[str]):
        if price > 0:
            payment_strategy = self.payment_factory.getPaymentService(payment_type)
            info_res = payment_strategy.set_information(payment_details)
            if info_res.success:
                payment_res = payment_strategy.pay(price)
                if not payment_res:
                    return report_error("purchase_shopping_cart", f"payment failed")
            else:
                return info_res

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str]) -> \
    Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = actor.verify_cart_not_empty()
        if response.success:
            baskets = actor.get_baskets()
            cart_price = 0
            successful_store_purchases = []

            for store_name, basket in baskets.items():
                response2 = self.verify_registered_store("purchase_shopping_cart", store_name)
                if response2.success:
                    store = response2.result
                    res = store.reserve_products(basket)
                    if res:
                        successful_store_purchases.append(store_name)
                        cart_price += store.calculate_basket_price(basket)


                else:
                    return response2

            self.pay(cart_price, payment_method, payment_details)
            self.update_user_cart_after_purchase(actor, successful_store_purchases)
        else:
            return response

        # TODO 2nd version - verify purchaser is conformed with store policy
        # TODO 2nd version - apply discount policy
