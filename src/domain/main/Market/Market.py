import random
import sys
from typing import Any, List

from src.domain.main.Store.StoreController import StoreController
from src.domain.main.User.UserController import UserController
from src.domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy
from src.domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.Store.PurchasePolicy.LotteryPolicy import LotteryPolicy
from src.domain.main.Store.PurchasePolicy.PurchasePolicyFactory import PurchasePolicyFactory
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
        self.user_controller.users.insert(name, admin)

    def __init__(self):
        self.user_controller: UserController = UserController()
        self.store_controller: StoreController = StoreController()
        self.payment_factory: PaymentFactory = PaymentFactory()
        self.init_admin()
        self.package_counter = 0
        self.PurchasePolicyFactory: PurchasePolicyFactory = PurchasePolicyFactory()

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.user_controller.sessions.get(identifier) is None:
                return identifier

    def enter(self) -> Session:
        session_identifier = self.generate_session_identifier()
        self.user_controller.sessions.insert(session_identifier, User(self))
        print('enter', self.user_controller.sessions.get(session_identifier))
        session = Session(session_identifier, self)
        Logger().post(f'{session} has been initialized', Logger.Severity.INFO)
        return session

    def get_all_stores(self, session_identifier: int) -> Response[List[Store]]:
        return self.store_controller.get_all_stores()

    def is_logged_in(self, username: str) -> bool:
        return self.user_controller.is_logged_in(username)

    def leave(self, identifier: int) -> Response[bool]:
        return self.user_controller.leave(identifier)
    def is_registered(self, username: str) -> bool:
        return self.user_controller.is_registered(username)
    def close_session(self, session_identifier: int) -> None:
        self.user_controller.sessions.delete(session_identifier)

    def shutdown(self, session_identifier: int) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = actor.is_allowed_to_shutdown_market()
        if response.success:
            # update days in stores for purchase policies:
            for store in self.store_controller.stores.to_string_keys().split(', '):
                self.store_controller.stores.get(store).new_day()
            Logger().post('Market is closed!', Logger.Severity.WARNING)
            Logger().shutdown()
            return response
        else:
            return response

    def register(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        new_user = User(self, username, encrypted_password)
        return self.user_controller.register(new_user,username)

    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        return self.user_controller.login(session_identifier, username, encrypted_password)

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = actor.logout()
        if response.success:
            self.user_controller.sessions.update(session_identifier, User(self))
        return response

    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        openStoreTuple = self.store_controller.open_store(store_name)
        if openStoreTuple[0] is None:
            actor = self.user_controller.get_active_user(session_identifier)
            response = actor.open_store(store_name)
            if not response.success:
                self.store_controller.delete_store(store_name)
            else:
                openStoreTuple[1].add_personal(actor.username)
                openStoreTuple[1].add_stock_personal(actor.username)
            return response
        return report_error(self.open_store.__qualname__, f'Store name \'{store_name}\' is occupied.')

    def get_store(self, session_identifier: int, store_name: str) -> Response[Store]:
        response = self.store_controller.verify_registered_store(store_name)
        if response.success:
            actor = self.user_controller.get_active_user(session_identifier)
            preface: str = f'Displaying store {response.result.name} to {actor}\n'
            return report(self.get_store.__qualname__ + preface + str(response.result.__dic__()),
                          response.result.__dic__())
        else:
            return response

    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        product = Product(product_name, category, price, keywords)
        response = actor.add_product(store_name)
        if response.success:
            response = self.store_controller.verify_registered_store(store_name)
            store = response.result
            return store.add(product, quantity) if response.success else response
        else:
            return response

    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> \
            Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = actor.update_product_quantity(store_name, product_name, quantity)
        if response.success:
            response = self.store_controller.verify_registered_store(store_name)
            store = response.result
            return store.update(product_name, quantity) if response.success else response
        else:
            return response

    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = actor.remove_product(store_name, product_name)
        if response.success:
            response = self.store_controller.verify_registered_store(store_name)
            store = response.result
            return store.remove(product_name) if response.success else response
        else:
            return response

    def add_to_cart(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = self.store_controller.verify_store_contains_product(self.add_to_cart.__qualname__, store_name, product_name)
        if response.success:
            store = response.result
            product_price = store.get_product_price(product_name)
            return actor.add_to_cart(store_name, product_name, product_price, quantity)
        else:
            return response

    def remove_product_from_cart(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = self.store_controller.verify_store_contains_product(self.remove_product_from_cart.__qualname__, store_name,
                                                      product_name)
        return actor.remove_product_from_cart(store_name, product_name) if response.success else response

    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str,
                                     quantity: int) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = self.store_controller.verify_store_contains_product(self.update_cart_product_quantity.__qualname__, store_name,
                                                      product_name)
        return actor.update_cart_product_quantity(store_name, product_name, quantity) if response.success else response

    def show_cart(self, session_identifier: int) -> Response[dict]:
        actor = self.user_controller.get_active_user(session_identifier)
        return actor.show_cart()

    def exit_market(self, session_identifier: int) -> Response[bool]:
        self.user_controller.sessions.delete(session_identifier)
        return report_info("exit", "no error")

    def update_user_cart_after_purchase(self, user: User, store_names: list) -> None:
        for store_name in store_names:
            user.empty_basket(store_name)


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
            self.store_controller.stores.get(store_name).add_to_purchase_history(basket)

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str],
                               address: str, postal_code: str) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_identifier)
        response = actor.verify_cart_not_empty()
        if response.success:
            baskets = actor.get_baskets()
            cart_price = 0
            successful_store_purchases = []

            for store_name, basket in baskets.items():
                response2 = self.store_controller.verify_registered_store(store_name)
                if response2.success:
                    store = response2.result
                    res = store.reserve_products(basket)
                    if res:
                        successful_store_purchases.append(store_name)
                        cart_price += store.calculate_basket_price(basket)
                else:
                    return response2.success
            payment_succeeded = self.pay(cart_price, payment_method, payment_details)
            if payment_succeeded:
                # order delivery
                delivery_service = provisionService()
                delivery_service.set_info(actor.username, 0, address, postal_code)
                if not delivery_service.getDelivery():
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
        actor = self.user_controller.get_active_user(session_id)
        response = actor.change_product_name(store_name, product_old_name)
        if response.success:
            response = self.store_controller.verify_registered_store(store_name)
            store = response.result
            return store.change_product_name(product_old_name, product_new_name) if response.success else response
        else:
            return response

    def change_product_price(self, session_id: int, store_name: str, product_old_price: float,
                             product_new_price: float) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_id)
        response = actor.change_product_price(store_name, product_old_price)
        if response.success:
            response = self.store_controller.verify_registered_store(store_name)
            store = response.result
            return store.change_product_price(product_old_price, product_new_price) if response.success else response
        else:
            return response

    def get_store_purchase_history(self, session_id: int, store_name: str = "") -> Response[bool]:
        actor = self.user_controller.get_active_user(session_id)
        actor.is_allowed_to_get_store_purchase_history(store_name)
        return self.store_controller.get_store_purchase_history(store_name)

    def close_store(self, session_id: int, store_name: str) -> Response[bool]:
        actor = self.user_controller.get_active_user(session_id)
        response = self.store_controller.verify_registered_store(store_name)
        if response.success:
            response = actor.close_store(store_name)
            if response.success:
                self.store_controller.delete_store(store_name)
            else:
                return response
        else:
            return response.success

    def get_products_by_category(self, session_id: int, category: str) -> Response[dict]:
        return self.store_controller.get_store_products_by_category(category)

    def get_products_by_name(self, session_id: int, name: str) -> Response[dict]:
        return self.store_controller.get_store_products_by_name(name);

    def get_products_by_keywords(self, session_id: int, keywords: list[str]) -> Response[dict]:
        return self.store_controller.get_store_products_by_keywords(keywords)

    def appoint_owner(self, session_id: int, new_owner_name: str, store_name: str) -> Response[bool]:
        r_final = self.user_controller.appoint_store_owner(session_id, new_owner_name, store_name)
        if r_final:
            self.store_controller.stores.get(store_name).add_personal(new_owner_name)
            self.store_controller.stores.get(store_name).add_stock_personal(new_owner_name)
        return r_final

    def appoint_manager(self, session_id: int, new_manager_name: str, store_name: str) -> Response[bool]:
        r_final = self.user_controller.appoint_store_manager(session_id, new_manager_name, store_name)
        if r_final.success:
            self.store_controller.stores.get(store_name).add_personal(new_manager_name)
            self.store_controller.stores.get(store_name).add_stock_personal(new_manager_name)
        return r_final

    def set_stock_permissions(self, session_id: int, receiving_user_name: str, store_name: str, give_or_take: bool) -> \
            Response[bool]:
        r_final = self.user_controller.stock_permissions(session_id, receiving_user_name, store_name, give_or_take)
        if r_final.success:
            if give_or_take:
                self.store_controller.stores.get(store_name).add_stock_personal(receiving_user_name)
            else:
                self.store_controller.stores.get(store_name).remove_stock_personal(receiving_user_name)
        return r_final

    def set_personal_permissions(self, session_id: int, receiving_user_name: str, store_name: str,
                                 give_or_take: bool) -> Response[bool]:
        return self.user_controller.personal_permissions(session_id, receiving_user_name, store_name, give_or_take)

    def get_store_personal(self, session_id: int, store_name: str) -> Response[str]:
        actor = self.user_controller.get_active_user(session_id)
        res = actor.is_allowed_to_view_store_personal(store_name)
        if not res.success:
            return res
        store = self.store_controller.stores.get(store_name)
        res = store.get_personal()
        return res

    def fire_employee(self, session_id: int, store_name: str, employee_name: str) -> Response[bool]:
        return self.user_controller.fire_employee(session_id, store_name, employee_name)

    # def add_purchase_policy_for_product(self, session_identifier: int, store_name: str, product_name: str,
    #                                     purchase_policy_name: str, purchase_policy_args: list) -> Response[bool]:
    #     actor = self.user_controller.get_active_user(session_identifier)
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
        actor = self.user_controller.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res
        return self.store_controller.start_auction(store_name, product_name, initial_price, duration)


    def start_lottery(self, session_id: int, store_name: str, product_name: str) -> \
            Response[bool] | Response[Store]:
        actor = self.user_controller.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res
        return self.store_controller.start_lottery(store_name, product_name)

    def start_bid(self, session_id: int, store_name: str, product_name: str) -> \
            Response[bool] | Response[Store]:
        actor = self.user_controller.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res
        return self.store_controller.start_bid(store_name, product_name)

    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float):
        actor = self.user_controller.get_active_user(session_identifier)

        payment_service = self.payment_factory.getPaymentService(payment_method)
        payment_service.set_information(payment_details)

        delivery_service = provisionService()
        delivery_service.set_info(actor.username, 0, address, postal_code, store_name)
        return self.store_controller.apply_purchase_policy(store_name, product_name, how_much,
                                                           payment_service, delivery_service)

    def approve_bid(self, session_id: int, store_name: str, product_name: str, is_approve: bool) -> Response:
        actor = self.user_controller.get_active_user(session_id)
        res = actor.add_product(store_name)  # verifying permissions for stock managing
        if not res.success:
            return res
        res = self.store_controller.verify_registered_store(store_name)
        if not res.success:
            return res
        store = res.result
        return store.approve_bid(actor.username, product_name, is_approve)
