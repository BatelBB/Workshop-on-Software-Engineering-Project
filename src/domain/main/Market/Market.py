import random
import sys
from typing import Any, List

from domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy
from domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy
from domain.main.Store.PurchasePolicy.LotteryPolicy import LotteryPolicy
from domain.main.Store.PurchasePolicy.PurchasePolicyFactory import PurchasePolicyFactory
from domain.main.Store.PurchaseRules import PurchaseRulesFactory
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
from src.domain.main.Store.PurchaseRules.PurchaseRulesFactory import *

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
        self.PurchasePolicyFactory: PurchasePolicyFactory = PurchasePolicyFactory()

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
            # update days in stores for purchase policies:
            for store in self.stores.to_string_keys().split(', '):
                self.stores.get(store).new_day()

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
                store.add_stock_personal(actor.username)

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
            return report(self.get_store.__qualname__ + preface + str(response.result.__dic__()),
                          response.result.__dic__())
        else:
            return response

    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:

        actor = self.get_active_user(session_identifier)
        product = Product(product_name, category, price, keywords)
        response = actor.add_product(store_name)
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

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str],
                               address: str, postal_code: str) -> \
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
            payment_succeeded = self.pay(cart_price, payment_method, payment_details)
            if payment_succeeded:
                # order delivery
                if not self.provision_service.getDelivery(actor.username, "remove", self.package_counter, address,
                                                          postal_code):
                    return report_error("purchase_shopping_cart", 'failed delivery')
                self.add_to_purchase_history(baskets)
                self.update_user_cart_after_purchase(actor, successful_store_purchases)
            else:
                return report_error("purchase_shopping_cart", "payment_succeeded = false")
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
        if r_final:
            self.stores.get(store_name).add_personal(new_owner_name)
            self.stores.get(store_name).add_stock_personal(new_owner_name)
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
        if r_final.success:
            self.stores.get(store_name).add_personal(new_manager_name)
            self.stores.get(store_name).add_stock_personal(new_manager_name)
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

        r_final = receiving_user.set_stock_permissions(store_name, give_or_take)
        if r_final.success:
            if give_or_take:
                self.stores.get(store_name).add_stock_personal(receiving_user_name)
            else:
                self.stores.get(store_name).remove_stock_personal(receiving_user_name)

        return r_final

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

    # def add_purchase_policy_for_product(self, session_identifier: int, store_name: str, product_name: str,
    #                                     purchase_policy_name: str, purchase_policy_args: list) -> Response[bool]:
    #     actor = self.get_active_user(session_identifier)
    #     res = actor.add_product(store_name)
    #     if not res.success:
    #         return res
    #
    #     res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
    #     if not res.success:
    #         return res
    #
    #     store = res.result
    #     policy = self.PurchasePolicyFactory.get_purchase_policy(purchase_policy_name, purchase_policy_args)
    #
    #     res = store.add_product_to_special_purchase_policy(product_name, policy)
    #     return res

    def start_auction(self, session_id: int, store_name: str, product_name: str, initial_price: float, duration: int) -> \
            Response[bool] | Response[Store]:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result
        policy = AuctionPolicy(initial_price, duration)

        return store.add_product_to_special_purchase_policy(product_name, policy)

    def start_lottery(self, session_id: int, store_name: str, product_name: str) -> \
            Response[bool] | Response[Store]:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result

        policy = LotteryPolicy(store.get_product_price(product_name))

        return store.add_product_to_special_purchase_policy(product_name, policy)

    def start_bid(self, session_id: int, store_name: str, product_name: str) -> \
            Response[bool] | Response[Store]:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result

        policy = BidPolicy()

        return store.add_product_to_bid_purchase_policy(product_name, policy)

    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float):
        actor = self.get_active_user(session_identifier)

        payment_service = self.payment_factory.getPaymentService(payment_method)
        payment_service.set_information(payment_details)

        delivery_service = provisionService()
        delivery_service.set_info(actor.username, store_name, 0, address, postal_code)

        res = self.verify_registered_store("purchase_with_non_immediate_policy", store_name)
        if not res.success:
            return res

        store = res.result
        res = store.apply_purchase_policy(payment_service, product_name, delivery_service, how_much)

        return res

    def approve_bid(self, session_id: int, store_name: str, product_name: str, is_approve: bool) -> Response:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result

        return store.approve_bid(actor.username, product_name, is_approve)

    def add_purchase_simple_rule(self, session_id: int, store_name: str, product_name: str, gle: str,
                                 amount: int) -> Response:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result

        rule = PurchaseRulesFactory.make_simple_rule(product_name, gle, amount)
        return store.add_purchase_rule(rule)

    def add_purchase_complex_rule(self, session_id: int, store_name: str, p1_name: str, gle1: str, amount1: int,
                                  p2_name: str, gle2: str, amount2: int,
                                  complex_rule_type: str) -> Response:
        actor = self.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res

        res = self.verify_registered_store("add_purchase_policy_for_product", store_name)
        if not res.success:
            return res
        store = res.result

        res = PurchaseRulesFactory.make_complex_rule(p1_name, gle1, amount1, p2_name, gle2, amount2, complex_rule_type)
        if res.success:
            return store.add_purchase_rule(res.result)
        return res


