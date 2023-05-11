import random
import sys
from typing import Any, List

from src.domain.main.ExternalServices.Payment.PaymentFactory import PaymentFactory
from src.domain.main.Store.Product import Product
from src.domain.main.Service.IService import IService
from src.domain.main.Store.Store import Store
from src.domain.main.User.Basket import Basket
from src.domain.main.User.Role.SystemAdmin import SystemAdmin
from src.domain.main.User.User import User
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Logger import report, Logger, report_error, report_info
from src.domain.main.Utils.Response import Response
from src.domain.main.Utils.Session import Session
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService, provisionService

# TODO: might be implemented as a Reactor: a singleton with a thread pool responsible for executing tasks
class Market(IService):

    # TODO: should be initialized with IPaymentService, IProvisionService
    def init_admin(self):
        name = "kfir"
        password = "kfir"
        admin = User(self, name, password)
        admin.role = SystemAdmin(admin)
        self.users.insert(name, admin)

    def __init__(self):
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.payment_factory: PaymentFactory = PaymentFactory()
        self.init_admin()
        self.provision_service: IProvisionService = provisionService()
        self.package_counter = 0

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.sessions.get(identifier) is None:
                return identifier

    def get_active_user(self, session_identifier: int) -> User | None:
        s = self.sessions.get(session_identifier)
        return s

    def enter(self) -> Session:
        session_identifier = self.generate_session_identifier()
        self.sessions.insert(session_identifier, User(self))
        print('enter', self.sessions.get(session_identifier))
        session = Session(session_identifier, self)
        Logger().post(f'{session} has been initialized', Logger.Severity.INFO)
        return session

    def close_session(self, session_identifier: int) -> None:
        self.sessions.delete(session_identifier)

    def shutdown(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = actor.is_allowed_to_shutdown_market()
        if response.success:
            Logger().post('Market is closed!', Logger.Severity.WARNING)
            Logger().shutdown()
            return response
        else:
            return response

    def verify_registered_store(self, calling_method_name: str, store_name: str) -> Response[Store]:
        store: Store = self.stores.get(store_name)
        return report(f'Entered verify register store function', store)

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
            return report_error(self.register.__qualname__, f'Username: {username} is occupied')

    def is_registered(self, username: str) -> bool:
        return self.users.get(username) is not None

    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        registered_user = self.users.get(username)
        if registered_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered)')
        else:
            response = registered_user.login(encrypted_password)
            if response.success:
                self.sessions.update(session_identifier, registered_user)
            return response

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in()

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = actor.logout()
        if response.success:
            self.sessions.update(session_identifier, User(self))
        return response

    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        store: Store = Store(store_name)
        registered_store_with_same_name = self.stores.insert(store_name, store)
        if registered_store_with_same_name is None:
            actor = self.get_active_user(session_identifier)
            response = actor.open_store(store_name)
            if not response.success:
                self.stores.delete(store_name)
            else:
                store.add_personal(actor.username)

            return response
        return report_error(self.open_store.__qualname__, f'Store name \'{store_name}\' is occupied.')

    def get_all_stores(self, session_identifier: int) -> Response[List[Store]]:
        stores = list(self.stores.dictionary.values())
        return report(f"displaying stores: {stores}", stores)

    def get_store(self, session_identifier: int, store_name: str) -> Response[dict] | Response[bool]:
        response = self.verify_registered_store(self.get_store.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_identifier)
            preface: str = f'Displaying store {response.result.name} to {actor}\n'
            return report(self.get_store.__qualname__ + preface + str(response.result.__dic__()), response.result.__dic__())
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

    def show_cart(self, session_identifier: int) -> Response[dict]:
        actor = self.get_active_user(session_identifier)
        return actor.show_cart()

    def exit_market(self, session_identifier: int) -> Response[bool]:
        self.sessions.delete(session_identifier)
        return report_info("exit", "no error")

    def update_user_cart_after_purchase(self, user: User, store_names: list) -> None:
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
            else:
                return info_res

    def add_to_purchase_history(self, baskets: dict[str, Any]) -> None:
        for store_name, basket in baskets.items():
            self.stores.get(store_name).add_to_purchase_history(basket)

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str], address: str, postal_code: str) -> \
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
            response3 = self.pay(cart_price, payment_method, payment_details)
            if response3.success:
                #order delivery
                if not self.provision_service.getDelivery(actor.username, "remove", self.package_counter, address, postal_code):
                    return report_error("purchase_shopping_cart", 'failed delivery')
                self.add_to_purchase_history(baskets)
                self.update_user_cart_after_purchase(actor, successful_store_purchases)
            else:
                return response3
        else:
            return response

        # TODO 2nd version - verify purchaser is conformed with store policy
        # TODO 2nd version - apply discount policy

    def change_product_name(self, session_id: int, store_name: str, product_old_name: str, product_new_name: str) -> \
            Response[bool]:
        actor = self.get_active_user(session_id)
        response = actor.change_product_name(store_name, product_old_name)
        if response.success:
            response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
            store = response.result
            return store.change_product_name(product_old_name, product_new_name) if response.success else response
        else:
            return response

    def change_product_price(self, session_id: int, store_name: str, product_old_price: float,
                             product_new_price: float) -> Response[bool]:
        actor = self.get_active_user(session_id)
        response = actor.change_product_price(store_name, product_old_price)
        if response.success:
            response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
            store = response.result
            return store.change_product_price(product_old_price, product_new_price) if response.success else response
        else:
            return response

    def get_store_purchase_history(self, session_id: int, store_name: str = "") -> Response[bool]:
        actor = self.get_active_user(session_id)
        actor.is_allowed_to_get_store_purchase_history(store_name)

        store = self.stores.get(store_name)
        return report_info(self.get_store_purchase_history.__qualname__, store.get_purchase_history())

    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_id)
        response = self.verify_registered_store(self.close_store.__qualname__, store_name)
        if response.success:
            response = actor.close_store(store_name)
            if response.success:
                self.stores.delete(store_name)
            else:
                return response
        else:
            return response

    def get_products_by_category(self, session_id: int, category: str) -> Response[dict]:
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_category(category)
            if product_dict:
                output[store_name] = product_dict

        report_info("get_products_by_category", f'products: {output}')
        return Response(output)

    def get_products_by_name(self, session_id: int, name: str) -> Response[dict]:
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_name(name)
            if product_dict:
                output[store_name] = product_dict

        report_info("get_products_by_name", f'products: {output}')
        return Response(output)

    def get_products_by_keywords(self, session_id: int, keywords: list[str]) -> Response[dict]:
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_keywords(keywords)
            if product_dict:
                output[store_name] = product_dict

        report_info("get_products_by_keywords", f'products: {output}')
        return Response(output)

    def get_registered_user(self, name: str) -> Response[User] | Response[bool]:
        if self.users.get(name) is not None:
            return Response(self.users.get(name))
        return Response(False)

    def appoint_owner(self, session_id: int, new_owner_name: str, store_name: str) -> Response[bool]:
        user_res = self.get_registered_user(new_owner_name)
        if not user_res.success:
            return user_res
        user = user_res.result

        actor = self.get_active_user(session_id)
        response = actor.is_allowed_to_appoint_owner(store_name, new_owner_name)
        if not response.success:
            return response

        r_final = user.make_me_owner(store_name)
        if r_final.success:
            self.stores.get(store_name).add_personal(new_owner_name)
        return r_final

    def appoint_manager(self, session_id: int, new_manager_name: str, store_name: str) -> Response[bool]:
        user_res = self.get_registered_user(new_manager_name)
        if not user_res.success:
            return user_res
        user = user_res.result

        actor = self.get_active_user(session_id)
        response = actor.is_allowed_to_appoint_manager(store_name, new_manager_name)
        if not response.success:
            return response

        r_final = user.make_me_owner(store_name)
        return r_final

    def set_stock_permissions(self, session_id: int, receiving_user_name: str, store_name: str, give_or_take: bool) -> \
            Response[bool]:
        actor = self.get_active_user(session_id)
        res = actor.is_allowed_to_change_permissions(store_name)
        if not res.success:
            return res

        receiving_user = self.get_registered_user(receiving_user_name)
        if not receiving_user.success:
            return receiving_user
        receiving_user = receiving_user.result

        return receiving_user.set_stock_permissions(store_name, give_or_take)

    def set_personal_permissions(self, session_id: int, receiving_user_name: str, store_name: str,
                                 give_or_take: bool) -> Response[bool]:
        actor = self.get_active_user(session_id)
        res = actor.is_allowed_to_change_permissions(store_name)
        if not res.success:
            return res

        receiving_user = self.get_registered_user(receiving_user_name)
        if not receiving_user.success:
            return receiving_user
        receiving_user = receiving_user.result

        return receiving_user.set_personal_permissions(store_name, give_or_take)

    def get_store_personal(self, session_id: int, store_name: str) -> Response[str]:
        actor = self.get_active_user(session_id)
        res = actor.is_allowed_to_view_store_personal(store_name)
        if not res.success:
            return res
        store = self.stores.get(store_name)
        res = store.get_personal()
        return res

    def fire_employee(self, session_id: int, store_name: str, employee_name: str) -> Response[bool]:
        actor = self.get_active_user(session_id)
        response = actor.is_allowed_to_fire_employee(store_name)
        if not response.success:
            return response
        else:
            user_res = self.get_registered_user(employee_name)
            if not user_res.success:
                return user_res
            user = user_res.result
            actor.appointees.get(store_name).remove(employee_name)
            for person in user.appointed_by_me:
                actor.appointees.get(store_name).remove(person)
            return response
