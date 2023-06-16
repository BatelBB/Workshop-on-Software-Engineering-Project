import random
import sys
import threading
from functools import reduce
from typing import Any

from multipledispatch import dispatch
from sqlalchemy import inspect
from Service.IService.IService import IService
from src.domain.main.Utils.InitExternalServices import init_external_services_from_configuration
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Cart import Cart
from src.domain.main.Utils.OwnersApproval import OwnersApproval
from src.domain.main.Notifications.notification_controller import NotificationController
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import provisionService, IProvisionService
from src.domain.main.Market.Appointment import Appointment
from src.domain.main.Market.Permissions import Permission, get_default_manager_permissions, \
    get_default_owner_permissions, \
    get_permission_description
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.PurchasePolicy.AuctionPolicy import AuctionPolicy
from src.domain.main.StoreModule.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.StoreModule.PurchasePolicy.LotteryPolicy import LotteryPolicy
from src.domain.main.StoreModule.PurchaseRules import PurchaseRulesFactory
from src.domain.main.StoreModule.Store import Store
from src.domain.main.UserModule.Basket import Item
from src.domain.main.UserModule.User import User
from src.domain.main.Utils.Base_db import Base, engine, init_db_from_configuration
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Logger import Logger, report_error, report_info
from src.domain.main.Utils.Response import Response
from src.Service.Session.Session import Session


class Market(IService):

    def __init__(self):
        self.provisionService = None
        self.paymentService = None
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.notifications = NotificationController()
        self.removed_stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.removed_store_products: ConcurrentDictionary[Store, set[Product]] = ConcurrentDictionary()
        self.removed_products_quantity: ConcurrentDictionary[Product, int] = ConcurrentDictionary()
        self.appointments: ConcurrentDictionary[str, list[Appointment]] = ConcurrentDictionary()
        self.store_activity_status: ConcurrentDictionary[str, str] = ConcurrentDictionary()
        self.package_counter = 0
        self.appointments_lock = threading.RLock()
        self.approval_lock = threading.RLock()
        self.approval_list: ConcurrentDictionary[
            str, ConcurrentDictionary[str, OwnersApproval]] = ConcurrentDictionary()
        self.init_db()
        self.init_admin()

    def init_db(self):
        Base.metadata.reflect(engine)
        classes_for_db = (User, Item, Store, Product, Appointment)
        tables_to_create = []

        for cls in classes_for_db:
            if not self.is_table_exsits(cls.__tablename__):
                tables_to_create.append(cls.__table__)

        Base.metadata.create_all(engine, checkfirst=True, tables=tables_to_create)

    def load_configuration(self, config):
        init_db_from_configuration(config['db'])
        payment_service, provision_service = init_external_services_from_configuration(config['external_services'])
        self.paymentService = payment_service
        self.provisionService = provision_service

    def is_table_exsits(self, table_name: str):
        inspector = inspect(engine)
        return inspector.has_table(table_name)

    def init_admin(self):
        admin_credentials = ('Kfir', 'Kfir', True)
        self.register(0, *admin_credentials)
        self.set_admin_permissions()

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.sessions.get(identifier) is None:
                return identifier

    def enter(self) -> Session:
        session_identifier = self.generate_session_identifier()
        self.sessions.insert(session_identifier, User())
        session = Session(session_identifier, self)
        Logger().post(f'{session} has been initialized')
        return session

    def get_active_user(self, session_identifier: int) -> User | None:
        return self.sessions.get(session_identifier)

    def has_a_role(self, username: str) -> bool:
        for store, appointments in self.appointments.get_all():
            for appointment in appointments:
                if appointment.appointed_by == username or appointment.appointee == username:
                    return True
        return False

    def get_store_appointments(self, store_name: str) -> list[Appointment]:
        appointments: list[Appointment] = self.appointments.get(store_name)
        return appointments if appointments is not None else []

    def get_appointment_of(self, username: str, store_name: str) -> Appointment | None:
        appointments = self.get_store_appointments(store_name)
        if appointments is not None:
            try:
                i = appointments.index(Appointment(username, store_name))
                return appointments[i]
            except Exception:
                return None
        return None

    def remove_appointment_of(self, fired_user: str, store_name: str) -> None:
        Appointment.delete_record(fired_user, store_name)
        self.appointments.get(store_name).remove(Appointment(fired_user, store_name))
        self.notifications.send_from_store(store_name, fired_user,
                                           f"The store {store_name} no longer requires your service. Sorry.")

    def get_appointees_of(self, fired_user: str, store_name: str) -> list[str]:
        appointments = filter(lambda appointment: appointment.appointed_by == fired_user,
                              self.appointments.get(store_name))
        return list(map(lambda appointment: appointment.appointee, appointments))

    def appointees_at(self, session_identifier: int, store_name: str) -> Response[list[str]]:
        actor = self.get_active_user(session_identifier)
        appointees = self.bfs(actor.username, store_name)
        appointees.remove(actor.username)
        msg = ', '.join(appointees)
        r = report_info(self.appointees_at.__qualname__, f'\'{actor}\' appointees at store \'{store_name}\': {msg}')
        return Response(appointees, r.description)

    def has_permission_at(self, store_name: str, actor: User, permission: Permission) -> bool:
        if actor is None:
            return False
        appointment = self.get_appointment_of(actor.username, store_name)
        return appointment is not None and appointment.is_allowed(permission)

    def is_not_appointed_yet(self, appointee: str, store_name: str) -> bool:
        return self.get_appointment_of(appointee, store_name) is None

    def add_appointment(self, store_name: str, appointment: Appointment) -> bool:
        appointments: list[Appointment] = self.appointments.get(store_name)
        with self.appointments_lock:
            if self.is_not_appointed_yet(appointment.appointee, store_name):
                Appointment.add_record(appointment)
                self.appointments.insert(store_name, [appointment]) if appointments is None else \
                    appointments.append(appointment)
                self.notifications.send_from_store(store_name, appointment.appointee,
                                                   f"The store {store_name} appointed you with permissions {appointment.permissions}")
                return True
            return False

    def add_store(self, store_name: str) -> Store | None:
        store = Store(store_name)
        registered_store_with_same_name = self.stores.insert(store_name, store)
        if registered_store_with_same_name is None:
            Store.add_record(store)
            return store
        return None

    def add_user(self, username, password, is_admin=False) -> User | None:
        user = User(username, password, is_admin)
        registered_user_with_same_name = self.users.insert(username, user)
        if registered_user_with_same_name is None:
            User.add_record(user)
            return user
        return None

    def is_appointed_by(self, appointee: str, appointed_by: str, store_name: str) -> bool:
        appointment = self.get_appointment_of(appointee, store_name)
        return appointment is not None and appointment.appointed_by == appointed_by

    def set_permissions_of(self, appointee: str, store: str, permission: Permission, action: {'ADD', 'REMOVE'}) -> bool:
        appointment = self.get_appointment_of(appointee, store)
        succeed = appointment is not None
        if succeed:
            appointment.add(permission) if action == 'ADD' else appointment.remove(permission)
        return succeed

    def is_founder_of(self, username: str, store_name: str) -> bool:
        ret = self.get_appointment_of(username, store_name)
        if ret is None:
            return False
        return ret.appointed_by is None

    def is_store_registered(self, store_name: str) -> bool:
        return self.find_store(store_name) is not None

    def shutdown(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_admin:
            for store in self.stores.get_all_values():
                store.new_day()
            Logger().post('Market is closed!', Logger.Severity.WARNING)
            Logger().shutdown()
            return report_info(self.shutdown.__qualname__, f'{actor} shutdown market')
        return report_error(self.shutdown.__qualname__, f'{actor} is not allowed to shutdown the market!')

    def verify_registered_store(self, calling_method_name: str, store_name: str) -> Response[Store] | Response[bool]:
        store: Store = self.find_store(store_name)
        return Response(store) if store is not None \
            else report_error(calling_method_name, f'Store \'{store_name}\' is not registered to the market.')

    def find_user(self, username) -> User | None:
        user = self.users.get(username)
        if user is None:
            user = User.load_user(username)
            if user is not None:
                self.users.insert(username, user)
        return user

    def find_store(self, store_name) -> Store | None:
        store = self.stores.get(store_name)
        if store is None:
            store = Store.load_store(store_name)
            if store is not None:
                self.stores.insert(store_name, store)
                self.appointments.insert(store_name, Appointment.load_appointments_of(store_name))
        return store

    def verify_registered_user(self, calling_method_name: str, username: str) -> Response[User] | Response[bool]:
        user: User = self.find_user(username)
        return Response(user) if user is not None \
            else report_error(calling_method_name, f'User \'{username}\' is not registered to the market.')

    def verify_registered_user_and_store(self, calling_method_name: str, username: str, store_name: str) -> Response[
        tuple[User, Store] | bool]:
        response = self.verify_registered_user(calling_method_name, username)
        if response.success:
            user = response.result
            response = self.verify_registered_store(calling_method_name, store_name)
            if response.success:
                store = response.result
                return Response((user, store))
            return response  # Unregistered store
        return response  # Unregistered user

    def get_all_registered_users(self) -> list[str]:
        return self.users.get_all_keys()

    def verify_store_contains_product(self, calling_method_name: str, store_name: str, product_name: str,
                                      quantity: int) -> Response[Store | bool]:
        response = self.verify_registered_store(calling_method_name, store_name)
        if response.success:
            store = response.result
            is_store_contains_product = store.contains(product_name)
            if is_store_contains_product:
                is_store_has_sufficient_quantity = store.amount_of(product_name) >= quantity
                if is_store_has_sufficient_quantity:
                    return Response(store)
                return report_error(self.verify_store_contains_product.__qualname__,
                                    f'Store \'{store_name}\' can provide only {store.amount_of(product_name)} units of Product \'{product_name}\'. Required: {quantity}.')
            return report_error(calling_method_name,
                                f'Store \'{store_name}\' does not contains Product \'{product_name}\'')
        return report_error(calling_method_name, f'Store \'{store_name}\' does not exist')

    def report_no_permission(self, calling_method: str, actor: User, store: str, permission: Permission):
        return report_error(calling_method,
                            f'\'{actor}\' has no permission to {get_permission_description(permission)} at store \'{store}\'')

    def leave(self, session_identifier: int) -> Response[bool]:
        leaving_user = self.sessions.delete(session_identifier)
        leaving_user.logout()
        return report_info(self.leave.__qualname__, f'{leaving_user} left session: {session_identifier}')

    def register(self, session_identifier: int, username: str, password: str, is_admin=False) -> Response[bool]:
        if self.find_user(username) is None:
            new_user = self.add_user(username, password, is_admin)
            if new_user is not None:
                return report_info(self.register.__qualname__, f'\'{new_user}\' is registered!')
        return report_error(self.register.__qualname__, f'Username: \'{username}\' is occupied')

    def is_registered(self, username: str) -> bool:
        return self.find_user(username) is not None

    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        next_user = self.find_user(username)
        if next_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered')
        if next_user.login(encrypted_password):
            current_user = self.get_active_user(session_identifier)
            if current_user.is_logged_in and current_user != next_user:
                current_user.logout()
            self.sessions.update(session_identifier, next_user)
            return report_info(self.login.__qualname__, f'{next_user} is logged in')
        return report_error(self.login.__qualname__, f'{username} failed to login: Incorrect password.')

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        self.sessions.insert(session_identifier, User())
        return actor.logout()

    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        store = self.find_store(store_name)
        if store is None:
            if actor.is_member():
                store = self.add_store(store_name)
                if store is not None:
                    self.add_appointment(store_name, Appointment(actor.username, store_name))
                    self.add_appointment(store_name, Appointment("Kfir", store_name, 'admin',
                                                                 permissions={Permission.RetrievePurchaseHistory}))
                    products_of_removed_store = self.removed_store_products.get(store)

                    if products_of_removed_store is not None:
                        for product in products_of_removed_store:
                            store.add(product, self.removed_products_quantity.get(product))

                    self.store_activity_status.insert(store_name, 'OPEN')
                    return report_info(self.open_store.__qualname__, f'{actor} opened store \'{store_name}\'.')
                return report_error(self.open_store.__qualname__, f'Store \'{store_name}\' is occupied.')
            return report_error(self.open_store.__qualname__, f'{actor} is not allowed to open a store.')
        return report_error(self.open_store.__qualname__, f'Store \'{store_name}\' is occupied.')

    def remove_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        store = self.find_store(store_name)
        if store is not None:
            if actor.is_member() and self.has_permission_at(store_name, actor, Permission.CloseStore):
                products = store.get_all()
                Store.delete_record(store_name)
                self.stores.delete(store_name)
                self.removed_stores.insert(store_name, store)
                self.removed_store_products.insert(store, products)
                for product in products:
                    self.removed_products_quantity.insert(product, store.amount_of(product.name))

                self.notifications.send_from_store(store_name, actor.username,
                                                   f"You have closed store {store_name}.")
                return report_info(self.remove_store.__qualname__, f'{actor} removed store {store_name}')
            else:
                return report_error(self.remove_store.__qualname__,
                                    f'{actor} is not allowed to remove store {store_name}')
        return report_error(self.remove_store.__qualname__, f'store {store_name} doesn\'t exist and can\'t be removed')

    def get_all_stores(self, session_identifier: int) -> Response[list[Store] | bool]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.get_all_stores.__qualname__,
                        f'Return all market stores to {actor}: {self.stores.to_string_keys()}')
        return Response(self.stores.get_all_values(), r.description)

    def get_all_deleted_stores(self, session_identifier: int) -> Response[list[Store] | bool]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.get_all_deleted_stores.__qualname__,
                        f'Return all market deleted stores to {actor}: {self.removed_stores.to_string_keys()}')
        return Response(self.removed_stores.get_all_values(), r.description)

    def get_store(self, session_identifier: int, store_name: str) -> Response[dict | bool]:
        response = self.verify_registered_store(self.get_store.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            r = report_info(self.get_store.__qualname__, f'Return store \'{store_name}\' to {actor}\n{store.__str__()}')
            return Response(store.__dic__(), r.description)
        return response

    def get_whole_store(self, session_identifier: int, store_name: str) -> Response[Store | bool]:
        response = self.verify_registered_store(self.get_whole_store.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            r = report_info(self.get_whole_store.__qualname__,
                            f'Return store \'{store_name}\' to {actor}\n{store.__str__()}')
            return Response(store, r.description)
        return response

    def get_all_products_of(self, session_identifier: int, store_name: str) -> Response[set[Product] | bool]:
        response = self.verify_registered_store(self.get_all_products_of.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            r = report_info(self.get_store.__qualname__, f'Return all store \'{store_name}\' products to {actor}')
            return Response(store.get_all(), r.description)
        return response

    def add_product(self, session_identifier: int, store_name: str, product_name: str, category: str,
                    price: float, quantity: int, keywords: list[str]) -> Response[bool]:
        response = self.verify_registered_store(self.add_product.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if price > 0:
                if self.has_permission_at(store_name, actor, Permission.Add):
                    p = Product(product_name, store_name, quantity, category, price, keywords)
                    store.add(p, quantity)
                    return report_info(self.add_product.__qualname__,
                                       f'\'{actor}\' add {quantity} units of {p} to store \'{store_name}\'')
                return self.report_no_permission(self.add_product.__qualname__, actor, store_name, Permission.Add)
            return report_error(self.add_product.__qualname__, f'Price cannot be less then zero!')
        return response

    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Remove):
                return report_info(self.remove_product.__qualname__,
                                   f'\'{actor}\' remove product \'{product_name}\' from store \'{product_name}\'') if store.remove(
                    product_name) \
                    else report_error(self.remove_product.__qualname__,
                                      f'\'{store_name}\' does not contains product \'{product_name}\'')
            return self.report_no_permission(self.remove_product.__qualname__, actor, store_name, Permission.Remove)
        return response

    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> \
            Response[bool]:
        response = self.verify_registered_store(self.update_product_quantity.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if quantity > 0:
                if self.has_permission_at(store_name, actor, Permission.Update):
                    return report_info(self.update_product_quantity.__qualname__,
                                       f'\'{actor}\' update product \'{product_name}\' at store \'{product_name}\' to {quantity} units') if store.update(
                        product_name, quantity) \
                        else report_error(self.update_product_quantity.__qualname__,
                                          f'\'{store_name}\' does not contains product \'{product_name}\'')
                return self.report_no_permission(self.update_product_quantity.__qualname__, actor, store_name,
                                                 Permission.Remove)
            return report_error(self.update_product_quantity.__qualname__, "Cannot update quantity to zero or negative")
        return response

    def get_amount_of(self, session_identifier: int, product_name: str, store_name: str) -> Response[int]:
        response = self.verify_registered_store(self.get_amount_of.__qualname__, store_name)
        store = response.result
        if store is not None:
            amount = store.amount_of(product_name)
            return Response(amount, f'Amount of \'{product_name}\' at store \'{store_name}\' is {amount}')
        return response

    def appoint(self, session_identifier: int, calling_method: str, store_name: str, appointee_name: str,
                required_permission: Permission, permissions: set[Permission],
                role: {'StoreManager', 'StoreOwner'}, original_appointer=None) -> Response[bool]:
        response = self.verify_registered_user_and_store(calling_method, appointee_name, store_name)
        if response.success:
            appointee, store = response.result
            actor = self.get_active_user(session_identifier)
            if not actor.is_member():
                return report_error(calling_method, f'{appointee} is not allowed to {required_permission.value}.')
            if self.has_permission_at(store_name, actor, required_permission):
                appointer = actor.username
                if original_appointer is not None:
                    appointer = original_appointer
                if self.add_appointment(store_name,
                                        Appointment(appointee_name, store_name, role, appointer, permissions)):
                    return report_info(calling_method, f'{actor} appointed \'{appointee.username}\' to a {role}.')
                return report_error(calling_method,
                                    f'{appointee} is already appointed to a role at store \'{store_name}\'.')
            return self.report_no_permission(calling_method, actor, store_name, required_permission)
        return response  # no registered appointee/store

    def get_product_by(self, session_identifier: int, calling_method: str, preidcate) -> Response[
        list[dict[str, dict]]]:
        actor = self.get_active_user(session_identifier)
        stores = self.stores.get_all_values()
        stores = [store for store in stores if self.store_activity_status.get(store.name) == 'OPEN' or
                  self.store_activity_status.get(store.name) == 'REOPEN']
        products_dictionaries = list(map(lambda store: store.get_products_by(preidcate), stores))
        msg = ''
        for i in range(len(stores)):
            if len(products_dictionaries[i]) > 0:
                msg += f'Store \'{stores[i].name}\'. Product: {products_dictionaries[i]}\n'
        r = report_info(calling_method, f'Return filtered products to {actor}:\n{msg}')
        return Response(products_dictionaries, r.description)

    def get_products_by_name(self, session_identifier: int, product_name: str) -> Response[list[dict[str, dict]]]:
        return self.get_product_by(session_identifier, self.get_products_by_name.__qualname__,
                                   lambda p: p.name == product_name)

    def get_products_by_category(self, session_identifier: int, category: str) -> Response[list[dict[str, dict]]]:
        return self.get_product_by(session_identifier, self.get_products_by_category.__qualname__,
                                   lambda p: p.category == category)

    def get_products_by_keywords(self, session_identifier: int, keywords: list[str]) -> Response[list[dict[str, dict]]]:
        return self.get_product_by(session_identifier, self.get_products_by_keywords.__qualname__,
                                   lambda p: len((set(p.keywords) & set(keywords))) > 0)

    def get_products_in_price_range(self, session_identifier: int, min: float, max: float) -> Response[
        list[dict[str, dict]]]:
        return self.get_product_by(session_identifier, self.get_products_in_price_range.__qualname__,
                                   lambda p: min <= p.price <= max)

    def appoint_manager(self, session_identifier: int, appointee_name: str, store_name: str) -> Response[bool]:
        return self.appoint(session_identifier, self.appoint_manager.__qualname__, store_name, appointee_name,
                            Permission.AppointManager, get_default_manager_permissions(), role='StoreManager')

    # only call from self.approve_owner or self.appoint_owner
    def add_owner(self, session_identifier: int, appointee_name: str, store_name: str) -> Response:
        approval = self.approval_list.get(store_name).get(appointee_name)
        if approval is None:
            appointer = None
        else:
            appointer = approval.starter

        res = self.appoint(session_identifier, self.add_owner.__qualname__, store_name, appointee_name,
                           Permission.AppointOwner, get_default_owner_permissions(), role='StoreOwner',
                           original_appointer=appointer)
        if res.success:
            store_res = self.verify_registered_store(self.add_owner.__qualname__, store_name)
            if not store_res.success:
                return report_error(self.add_owner.__qualname__, "invalid store")

            store = store_res.result
            store.add_owner(appointee_name)

            store_dict = self.approval_list.get(store_name)
            for name in store_dict.get_all_keys():
                store_dict.get(name).add_owner(appointee_name)

            store_dict.delete(appointee_name)
        return res

    def approve_owner(self, session_identifier: int, appointee_name: str, store_name: str, is_approve: bool) -> \
            Response[bool]:
        with self.approval_lock:
            actor = self.get_active_user(session_identifier)
            perms = self.permissions_of(session_identifier, store_name, actor.username)
            if Permission.AppointOwner not in perms.result:
                return report_error(self.appoint_owner.__qualname__,
                                    f"{actor.username} does not have permissions to appoint owner")

            store_dict = self.approval_list.get(store_name)
            if store_dict is None:
                return report_error(self.approve_owner.__qualname__, "approval doesnt exist")
            approval = store_dict.get(appointee_name)
            if approval is None:
                return report_error(self.approve_owner.__qualname__, "approval doesnt exist")

            if is_approve:
                approval_res = approval.approve(actor.username)
                if not approval_res.result:
                    return report_info(self.approve_owner.__qualname__, f"{actor.username} approved")

                # store_dict.delete(appointee_name)
                return self.add_owner(session_identifier, appointee_name, store_name)
            else:
                store_dict.delete(appointee_name)
                return report_info(self.approve_owner.__qualname__, "approval declined successfully")

    def appoint_owner(self, session_identifier: int, appointee_name: str, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        perms = self.permissions_of(session_identifier, store_name, actor.username)

        if not perms.success:
            return perms
        if Permission.AppointOwner not in perms.result:
            return report_error(self.appoint_owner.__qualname__,
                                f"{actor.username} does not have permissions to appoint owner")

        store = self.verify_registered_store(self.appoint_owner.__qualname__, store_name)
        if not store.success:
            return store
        owners = self.get_store_owners(session_identifier, store_name).result
        if appointee_name in owners:
            return report_error(self.appoint_owner.__qualname__, f"{appointee_name} is already owner of {store_name}")

        if store_name not in self.approval_list.list_keys():
            self.approval_list.insert(store_name, ConcurrentDictionary())

        if appointee_name in self.approval_list.get(store_name).list_keys():
            return self.approve_owner(session_identifier, appointee_name, store_name, True)

        approval = OwnersApproval(owners, actor.username)

        if approval.is_approved().result:
            return self.add_owner(session_identifier, appointee_name, store_name)

        self.approval_list.get(store_name).insert(appointee_name, approval)
        return report_info(self.appoint_owner.__qualname__,
                           f"approval process beggins for ownership for {appointee_name} of {store_name}")

    def set_permission(self, session_identifier: int, calling_method: str, store: str, appointee: str,
                       permission: Permission, action: {'ADD', 'REMOVE'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if self.is_appointed_by(appointee, actor.username, store):
            self.set_permissions_of(appointee, store, permission, action)
            return report_info(calling_method,
                               f'\'{actor}\' {action} permission {get_permission_description(permission)} to \'{appointee}\'')
        return report_error(calling_method, f'\'{appointee}\' is not appointed by \'{actor}\'')

    def add_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> Response[
        bool]:
        return self.set_permission(session_identifier, self.add_permission.__qualname__, store, appointee, permission,
                                   'ADD')

    def remove_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> \
            Response[bool]:
        return self.set_permission(session_identifier, self.remove_permission.__qualname__, store, appointee,
                                   permission, 'REMOVE')

    def permissions_of(self, session_identifier: int, store: str, subject: str) -> Response[set[Permission] | bool]:
        appointment = self.get_appointment_of(subject, store)
        actor = self.get_active_user(session_identifier)
        if appointment is not None:
            r = report_info(self.permissions_of.__qualname__,
                            f'Display permission of \'{subject}\' at store \'{store}\' to {actor}')
            return Response(appointment.permissions, r.description)
        return report_error(self.permissions_of.__qualname__, f'\'{subject}\' has no role at store \'{store}\'')

    def get_admin_permissions(self) -> Response[set[Permission] | bool]:
        r = report_info(self.permissions_of.__qualname__,
                        f'Display permission of admin')
        return Response(get_default_owner_permissions(), r.description)

    def bfs(self, root: str, store_name: str) -> list[str]:
        """
        Store appointments creates a tree
        We iterate over the subtree of root in a breath-first-manner to aggregate all its successive appointees
        """
        successors: list[str] = list()
        queue: list[str] = list()
        queue.append(root)
        while len(queue) > 0:
            parent = queue.pop()
            successors.append(parent)
            for successor in self.get_appointees_of(parent, store_name):
                queue.append(successor)
        return successors

    def update_owner_approvals(self, fired, store_name):
        # update approval_list: remove approvals started by fired, remove_owner from all approvals for this store
        store_dict = self.approval_list.get(store_name)
        if store_dict is not None:
            for key in store_dict.get_all_keys():
                approval = store_dict.get(key)
                if approval.starter == fired:
                    store_dict.delete(key)
                else:
                    store_dict.get(key).remove_owner(fired)
        # update bid approvals in store:
        store = self.verify_registered_store("update_owner_approvals", store_name)
        if not store.success:
            return report_error("update_owner_approvals", f"{store_name} store not found")
        store = store.result
        store.remove_owner(fired)

    def remove_appointment(self, session_identifier: int, fired_appointee: str, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if self.is_appointed_by(fired_appointee, actor.username, store_name):
            fired_appointee_successors = self.bfs(fired_appointee, store_name)
            fired_appointee_successors_msg = ', '.join(fired_appointee_successors)
            [self.update_owner_approvals(fired, store_name) for fired in fired_appointee_successors]
            [self.remove_appointment_of(fired, store_name) for fired in fired_appointee_successors]
            return report_info(self.remove_appointment.__qualname__,
                               f'\'{actor}\' remove appointment of \'{fired_appointee_successors_msg}\' at store \'{store_name}\'.')
        return report_error(self.remove_appointment.__qualname__,
                            f'\'{fired_appointee}\' is not appointed by {actor} at store {store_name}')

    def set_store_activity_status(self, session_identifier: int, calling_method: str, store_name: str, is_active: bool,
                                  action: {'CLOSED', 'REOPEN'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_member():
            if self.is_founder_of(actor.username, store_name):
                for appointment in self.get_store_appointments(store_name):
                    appointment.is_store_active = is_active  # TODO: notify appointee
                self.store_activity_status.insert(store_name, action)
                return report_info(calling_method, f'Founder \'{actor}\' {action} store \'{store_name}\'')
            return report_error(calling_method, f'\'{actor}\' is not the founder of store \'{store_name}\'')
        return report_error(calling_method, f'Visitor attempted to {action} store \'{store_name}\'')

    def close_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        if self.store_activity_status.get(store_name) != 'CLOSED':
            return self.set_store_activity_status(session_identifier, self.close_store.__qualname__, store_name, False,
                                                  'CLOSED')
        return report_error(self.close_store.__qualname__, f'You tried to close {store_name} but it\'s already closed')

    def reopen_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        if self.store_activity_status.get(store_name) != 'REOPEN':
            return self.set_store_activity_status(session_identifier, self.reopen_store.__qualname__, store_name, True,
                                                  'REOPEN')
        return report_error(self.reopen_store.__qualname__,
                            f'You tried to reopen {store_name} but it\'s already reopened')

    def staff_to_string(self, appointments: list[Appointment]) -> str:
        out = ''
        i = 1
        for appointment in appointments:
            out += f'{i})\t{appointment}\n'
            i += 1
        return out

    @dispatch(int, str)
    def get_store_staff(self, session_identifier: int, store_name: str) -> Response[list[Appointment] | bool]:
        response = self.verify_registered_store(self.get_store_appointments.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.RetrieveStaffDetails):
                appointments = self.get_store_appointments(store_name)
                r = report_info(self.get_store_appointments.__qualname__,
                                f'Display store \'{store_name}\' staff to {actor}\nStaff\n{self.staff_to_string(appointments)}')
                return Response(appointments, r.description)
            return self.report_no_permission(self.get_store_appointments.__qualname__, actor, store_name,
                                             Permission.RetrieveStaffDetails)
        return response

    @dispatch(str)
    def get_store_staff(self, store_name: str) -> list[str]:
        appointments = self.get_store_appointments(store_name)
        return reduce(lambda acc, appointment: acc.append(appointment.appointee), appointments, [])

    def get_store_personal(self, session_identifier: int, store_name: str) -> Response[str | bool]:
        response = self.get_store_staff(session_identifier, store_name)
        return Response(response.description) if response.success else response

    def add_to_cart(self, session_identifier: int, store_name: str, product: str, quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.add_to_cart.__qualname__, store_name, product, quantity)
        if response.success:
            store = response.result
            price = store.get_product_price(product)
            return actor.add_to_cart(store_name, product, price, quantity) if price > 0 \
                else report_error(self.add_to_cart.__qualname__,
                                  f'Store \'{store}\' does not contains product \'{product}\'')
        return response

    def remove_product_from_cart(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.remove_product_from_cart.__qualname__, store_name,
                                                      product_name, 1)
        return actor.remove_product_from_cart(store_name, product_name) if response.success else response

    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str,
                                     quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.update_cart_product_quantity.__qualname__, store_name,
                                                      product_name, quantity)
        return actor.update_cart_product_quantity(store_name, product_name, quantity) if response.success else response

    def change_product_name(self, session_identifier: int, store_name: str, product_old_name: str,
                            product_new_name: str) -> Response[bool]:
        response = self.verify_registered_store(self.change_product_name.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Update):
                if store.change_product_name(product_old_name, product_new_name):
                    return report_info(self.change_product_name.__qualname__,
                                       f'Product \'{product_old_name}\' changed to \'{product_new_name}\' at store \'{store_name}\' by {actor}')
                return report_error(self.change_product_name.__qualname__,
                                    f'Store \'{store_name}\' does not contains product \'{product_old_name}\'')
            return self.report_no_permission(self.change_product_name.__qualname__, actor, store_name,
                                             Permission.Update)
        return response

    def change_product_price(self, session_identifier: int, store_name: str, product_old_price: float,
                             product_new_price: float) -> Response[bool]:
        response = self.verify_registered_store(self.change_product_price.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            if product_new_price > 0:
                if self.has_permission_at(store_name, actor, Permission.Update):
                    store.change_product_price(product_old_price, product_new_price)
                    return report_info(self.change_product_price.__qualname__,
                                       f'Product of price {product_old_price} changed to \'{product_new_price}\' at store \'{store_name}\' by {actor}')
                return self.report_no_permission(self.change_product_price.__qualname__, actor, store_name,
                                                 Permission.Update)
            return report_error(self.change_product_price.__qualname__, "Price cannot be zero or negative!")
        return response

    def change_product_category(self, session_identifier: int, store_name: str, product_name: str, category: str) -> \
            Response[bool]:
        response = self.verify_registered_store(self.change_product_category.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Update):
                if store.change_product_category(product_name, category):
                    return report_info(self.change_product_category.__qualname__,
                                       f'Product {product_name} category changed to \'{category}\' at store \'{store_name}\' by {actor}')
                return report_error(self.change_product_name.__qualname__,
                                    f' Store \'{store_name}\' does not contains product \'{product_name}\'')
            return self.report_no_permission(self.change_product_category.__qualname__, actor, store_name,
                                             Permission.Update)
        return response

    def show_cart(self, session_identifier: int) -> Response[dict | bool]:
        actor = self.get_active_user(session_identifier)
        self.update_item_prices(actor)
        r = actor.show_cart()
        report_info(self.show_cart.__qualname__, r.description)
        return r

    def update_item_prices(self, actor: User):
        baskets = actor.get_baskets()
        for store_name, basket in baskets.items():
            response = self.verify_registered_store(self.update_item_prices.__qualname__, store_name)
            if not response.success:
                return response
            store = response.result
            store.calculate_basket_price(basket)

    def get_cart(self, session_identifier: int) -> Response[Cart]:
        actor = self.get_active_user(session_identifier)
        self.update_item_prices(actor)
        r = report_info(self.get_cart.__qualname__, f'Cart of {actor}\n{actor.cart}')
        return Response(actor.cart, r.description)

    def cancel_membership_of(self, session_identifier: int, member_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_admin:
            response = self.verify_registered_user(self.cancel_membership_of.__qualname__, member_name)
            if response.success:
                member = response.result
                if not self.has_a_role(member_name):
                    member.cancel_membership()
                    return report_info(self.cancel_membership_of.__qualname__,
                                       f'\'{member_name}\' membership is dismissed')
                return report_error(self.cancel_membership_of.__qualname__,
                                    f'\'{member_name}\' has a role at the market')
            return response
        return report_error(self.cancel_membership_of.__qualname__, f'\'{actor}\' is not an admin')

    def clear(self) -> None:
        User.clear_db()
        Store.clear_db()
        Appointment.clear_db()
        self.__init__()

    def pay(self, price: int, payment_details: list[str], holder: str, user_id: int):
        if price > 0:
            try:
                info_res = self.paymentService.set_information(payment_details, holder, user_id)
                if info_res.success:
                    payment_res = self.paymentService.pay(price)
                    if not payment_res:
                        report_error(self.pay.__qualname__, f'paying failed')
                    else:
                        return payment_res
                else:
                    report_error(self.pay.__qualname__, f'setting payment information failed {info_res}')
            except Exception as e:
                report_error(self.pay.__qualname__, f"failed to get payment service {e}")

    def add_to_purchase_history(self, baskets: dict[str, Any]) -> None:
        for store_name, basket in baskets.items():
            self.find_store(store_name).add_to_purchase_history(basket)

    def update_user_cart_after_purchase(self, user: User, store_names: list) -> None:
        for store_name in store_names:
            user.empty_basket(store_name)

    def get_cart_price(self, baskets):
        cart_price = 0

        for store_name, basket in baskets.items():
            response2 = self.verify_registered_store(self.get_cart_price.__qualname__, store_name)
            if response2.success:
                store = response2.result
                res = store.check_rules(basket)
                if res.success and res.result:
                    cart_price += store.calculate_basket_price(basket)
            else:
                return response2.success
        return cart_price

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str],
                               address: str, postal_code: str, city: str, country: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        holder = actor.username
        user_id = actor.get_user_id()
        response = actor.verify_cart_not_empty()
        successful_store_purchases = []
        if response.success:
            baskets = actor.get_baskets()
            for store_name, basket in baskets.items():
                store = self.stores.get(store_name)
                res = store.reserve_products(basket)
                if res.success and res.result:
                    successful_store_purchases.append(store_name)
            resp = self.get_cart_price(baskets)
            payment_succeeded = self.pay(resp, payment_details, holder, user_id)
            if payment_succeeded:
                # order delivery
                self.provisionService.set_info(actor.username, 0, address, postal_code, city, country)
                if not self.provisionService.getDelivery():
                    self.paymentService.refund(resp)
                    return report_error(self.purchase_shopping_cart.__qualname__, 'failed delivery')
                successful_baskets = {store_name: basket for store_name, basket in baskets.items() if store_name in successful_store_purchases}
                self.add_to_purchase_history(successful_baskets)
                self.update_user_cart_after_purchase(actor, successful_store_purchases)
                for store_name, basket in baskets.items():
                    self.find_store(store_name).update_db(basket)
                return Response(True)
            else:
                return report_error(self.purchase_shopping_cart.__qualname__, "payment_succeeded = false")
        else:
            return response

    def get_store_purchase_history(self, session_id: int, store_name: str) -> list[str] | Response[bool]:
        response = self.verify_registered_store(self.get_store_purchase_history.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_id)
            store = response.result
            if self.has_permission_at(store_name, actor, Permission.RetrievePurchaseHistory):
                return store.get_purchase_history()
            return self.report_no_permission(self.get_store_purchase_history.__qualname__, actor, store_name,
                                             Permission.RetrievePurchaseHistory)
        return report_error(self.get_store_purchase_history.__qualname__, response.description)

    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str):
        response = self.verify_registered_store(self.purchase_with_non_immediate_policy.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            holder = actor.username
            user_id = actor.get_user_id()
            payment_service = self.paymentService
            provision_service = self.provisionService
            payment_service.set_information(payment_details, holder, user_id)
            provision_service.set_info(actor.username, 0, address, postal_code, city, country, store_name)
            return store.apply_purchase_policy(payment_service, product_name, provision_service, how_much)

    def start_auction(self, session_id: int, store_name: str, product_name: str, initial_price: float, duration: int) -> \
            Response[Store | bool]:
        response = self.verify_registered_store(self.start_auction.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.OpenAuction):
                policy = AuctionPolicy(initial_price, duration)
                return store.add_product_to_special_purchase_policy(product_name, policy)
            return self.report_no_permission(self.start_auction.__qualname__, actor, store_name, Permission.OpenAuction)
        return response

    def start_lottery(self, session_id: int, store_name: str, product_name: str) -> Response[Store | bool]:
        response = self.verify_registered_store(self.start_lottery.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.OpenLottery):
                policy = LotteryPolicy(store.get_product_price(product_name))
                return store.add_product_to_special_purchase_policy(product_name, policy)
            return self.report_no_permission(self.start_lottery.__qualname__, actor, store_name, Permission.OpenLottery)
        return response

    def start_bid(self, session_id: int, store_name: str, product_name: str) -> Response[Store | bool]:
        response = self.verify_registered_store(self.start_bid.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.StartBid):
                owners_list_res = self.get_store_owners(session_id, store_name)
                if not owners_list_res.success:
                    return owners_list_res

                approval = OwnersApproval(owners_list_res.result, actor.username)
                policy = BidPolicy(approval)
                return store.add_product_to_bid_purchase_policy(product_name, policy)
            return self.report_no_permission(self.start_bid.__qualname__, actor, store_name, Permission.StartBid)
        return response

    def approve_bid(self, session_id: int, store_name: str, product_name: str, is_approve: bool) -> Response:
        response = self.verify_registered_store(self.approve_bid.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.ApproveBid):
                return store.approve_bid(actor.username, product_name, is_approve)
            return self.report_no_permission(self.approve_bid.__qualname__, actor, store_name, Permission.StartBid)
        return response

    def rule_maker(self, rule_type: str, p1_name: str = None, gle1: str = None, amount1: int = None,
                   p2_name: str = None,
                   gle2: str = None, amount2: int = None, min_price: float = None) -> Response[IRule]:
        if rule_type == "basket":
            return PurchaseRulesFactory.make_basket_rule(min_price)
        elif rule_type == "simple":
            return PurchaseRulesFactory.make_simple_rule(p1_name, gle1, amount1)
        elif rule_type == "and" or rule_type == "or":
            return PurchaseRulesFactory.make_complex_rule(p1_name, gle1, amount1, p2_name, gle2, amount2, rule_type)
        else:
            report_error(self.rule_maker.__qualname__, f"no such rule type: {rule_type}")

    def add_purchase_simple_rule(self, session_id: int, store_name: str, product_name: str, gle: str,
                                 amount: int) -> Response:
        response = self.verify_registered_store(self.add_purchase_simple_rule.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.AddRule):
                rule = PurchaseRulesFactory.make_simple_rule(product_name, gle, amount)
                return store.add_purchase_rule(rule.result)
            return self.report_no_permission(self.add_purchase_simple_rule.__qualname__, actor, store_name,
                                             Permission.AddRule)
        return response

    def add_purchase_complex_rule(self, session_id: int, store_name: str, p1_name: str, gle1: str, amount1: int,
                                  p2_name: str, gle2: str, amount2: int,
                                  complex_rule_type: str) -> Response:
        response = self.verify_registered_store(self.add_purchase_complex_rule.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.AddRule):
                rule = PurchaseRulesFactory.make_complex_rule(p1_name, gle1, amount1, p2_name, gle2, amount2,
                                                              complex_rule_type)
                return store.add_purchase_rule(rule.result)
            return self.report_no_permission(self.add_purchase_complex_rule.__qualname__, actor, store_name,
                                             Permission.AddRule)
        return response

    def apply_purchase_policy(self, store_name: str, product_name: str, how_much: float,
                              payment_service: IPaymentService,
                              delivery_service: IProvisionService):
        response = self.verify_registered_store(self.apply_purchase_policy.__qualname__, store_name)
        if response.success:
            store = response.result
            return store.apply_purchase_policy(payment_service, product_name, delivery_service, how_much)
        return response

    def add_simple_discount(self, session_id: int, store_name: str, discount_type: str, discount_percent: int,
                            discount_for_name: str = None,
                            rule_type=None, min_price: float = None,
                            p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None) -> Response:
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.add_simple_discount.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.add_simple_discount.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.add_simple_discount.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangeDiscountPolicy not in perms:
            return report_error(self.add_simple_discount.__qualname__, f"{actor} has no permission to add discount")

        rule = None
        if rule_type is not None and rule_type != 'None':
            rule = self.rule_maker(rule_type, p1_name, gle1, amount1, p2_name, gle2, amount2, min_price)
            if not rule.success:
                return rule
            rule = rule.result

        return store.add_simple_discount(discount_percent, discount_type, rule, discount_for_name)

    def connect_discounts(self, session_id: int, store_name, id1, id2, connection_type, rule_type=None,
                          min_price: float = None,
                          p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.add_simple_discount.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.connect_discounts.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.connect_discounts.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangeDiscountPolicy not in perms:
            return report_error(self.connect_discounts.__qualname__, f"{actor} has no permission to add discount")

        rule = None
        if rule_type is not None and rule_type != "None":
            rule = self.rule_maker(rule_type, p1_name, gle1, amount1, p2_name, gle2, amount2, min_price)
            if not rule.success:
                return rule
            rule = rule.result

        return store.connect_discounts(id1, id2, connection_type, rule)

    def get_purchase_rules(self, session_id: int, store_name: str) -> Response[dict[int:IRule]]:
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.get_purchase_rules.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.get_purchase_rules.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.get_purchase_rules.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangePurchasePolicy not in perms:
            return report_error(self.get_purchase_rules.__qualname__,
                                f"{actor} has no permission to manage purchase rules")

        return Response(store.get_purchase_rules(), "purchase rules")

    def delete_purchase_rule(self, session_id: int, store_name: str, index: int):
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.delete_purchase_rule.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.delete_purchase_rule.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.delete_purchase_rule.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangePurchasePolicy not in perms:
            return report_error(self.delete_purchase_rule.__qualname__,
                                f"{actor} has no permission to manage purchase rules")

        return store.remove_purchase_rule(index)

    def add_basket_purchase_rule(self, session_id: int, store_name: str, min_price: float):
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.add_basket_purchase_rule.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.add_basket_purchase_rule.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.add_basket_purchase_rule.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangePurchasePolicy not in perms:
            return report_error(self.add_basket_purchase_rule.__qualname__,
                                f"{actor} has no permission to manage purchase rules")

        rule = self.rule_maker("basket", min_price=min_price)
        return store.add_purchase_rule(rule.result)

    def get_discounts(self, session_id: int, store_name: str) -> Response:
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.get_discounts.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.get_discounts.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.get_discounts.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangeDiscountPolicy not in perms:
            return report_error(self.get_discounts.__qualname__, f"{actor} has no permission to manage discounts")

        return Response(store.get_discounts(), "discounts")

    def delete_discount(self, session_id: int, store_name: str, index: int):
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.delete_discount.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.delete_discount.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.delete_discount.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangeDiscountPolicy not in perms:
            return report_error(self.delete_discount.__qualname__, f"{actor} has no permission to manage discounts")

        return store.delete_discount(index)

    def get_store_owners(self, session_id: int, store_name: str) -> Response[bool] | Response[list[str]]:
        actor = self.get_active_user(session_id)
        res = self.get_store_staff(session_id, store_name)
        if not res.success:
            return res
        staff = res.result
        owners = []
        for appoitment in staff:
            p = appoitment.appointee
            perms = self.permissions_of(session_id, store_name, p)
            if not perms.success:
                return report_error(self.get_store_owners.__qualname__, "failed to retrieve permissions")
            perms = perms.result
            if Permission.AppointOwner in perms:
                owners.append(p)

        return Response(owners, "list of owners")

    def get_store_managers(self, session_id: int, store_name: str) -> Response[bool] | Response[list[str]]:
        res = self.get_store_staff(session_id, store_name)
        if not res.success:
            return res
        staff = res.result
        managers = []
        default_manager_permissions = get_default_manager_permissions()
        for appoitment in staff:
            p = appoitment.appointee
            perms_res = self.permissions_of(session_id, store_name, p)
            if not perms_res.success:
                return report_error(self.get_store_managers.__qualname__, "failed to retrieve permissions")
            perms = perms_res.result

            if perms == default_manager_permissions:
                managers.append(p)

        return Response(managers, "list of managers")

    ### only for testing purposes:
    def approve_as_owner_immediatly(self, session_id, store_name, appointee_name):
        store_dict = self.approval_list.get(store_name)
        approval = store_dict.get(appointee_name)
        if approval is not None:
            for person in approval.to_approve.keys():
                approval.approve(person)

            store_dict.delete(appointee_name)
            self.add_owner(session_id, appointee_name, store_name)

    def get_active_session_id(self, username):
        for sess_id in self.sessions.get_all_keys():
            if self.sessions.get(sess_id).username == username:
                return sess_id
        return None

    def send_user_message(self, session_id: int, recipient: str, content: str):
        actor = self.get_active_user(session_id)
        if not actor.is_logged_in:
            return report_error(self.send_user_message.__qualname__, "Can't send message: not logged in")
        if recipient not in self.users.get_all_keys():
            return report_error(self.send_user_message.__qualname__, "no such user")
        self.notifications.send_from_user(actor.username, recipient, content)
        return report_info(self.send_user_message.__qualname__,
                           f"send message succesful: {actor.username} -> {recipient}: {content}")

    def get_user_unread_observable(self, session_id: int):
        actor = self.get_active_user(session_id)
        if not actor.is_logged_in:
            return report_error(self.send_user_message.__qualname__, "Can't get unread observable: not logged in")
        return Response(self.notifications.get_unread_observable(actor.username))

    def get_inbox(self, session_id: int):
        actor = self.get_active_user(session_id)
        if not actor.is_logged_in:
            return report_error(self.send_user_message.__qualname__, "Can't get inbox: not logged in")
        return Response(self.notifications.get_notifications_for(actor.username))

    def mark_read(self, session_id: int, msg_id: int):
        actor = self.get_active_user(session_id)
        if not actor.is_logged_in:
            return report_error('mark_read', "mark_read: not logged in")
        msg = self.notifications.mark_read(actor.username, msg_id)
        return msg

    def get_store_staff_wit_permissions(self, session_id: int, store_name: str):
        staff_permissions = {}
        resp = self.get_store_staff(session_id, store_name)
        if resp.success:
            resp = resp.result
            for person in resp:
                permissions = self.permissions_of(session_id, store_name, person.appointee).result
                staff_permissions[person.appointee] = permissions
            return staff_permissions

    '''
        Validation methods - used to compare ram object against DB records
    '''

    def get_number_of_registered_users(self) -> int:
        return self.users.size() - 1 if self.users.size() == User.number_of_records() else -1  # ignore default admin user

    def get_number_of_stores(self) -> int:
        return self.stores.size() if self.stores.size() == Store.number_of_records() else -1

    def get_number_of_products(self):
        return Product.number_of_records()

    def get_number_of_items(self):
        return Item.number_of_records()

    def get_user_from_ram(self, username) -> User | None:
        return self.users.get(username)

    def get_user_from_db(self, username) -> User | None:
        return User.load_user(username)

    def verify_user_consistent(self, username) -> bool:
        u1, u2 = self.get_user_from_ram(username), self.get_user_from_db(username)
        return u1 is None and u2 is None or \
            u1 is not None and u2 is not None and u1.username == u2.username and u1.encrypted_password == u2.encrypted_password

    def get_store_from_ram(self, store_name) -> Store | None:
        return self.stores.get(store_name)

    def get_store_from_db(self, store_name) -> Store | None:
        return Store.load_store(store_name)

    def verify_store_consistent(self, store_name) -> bool:
        s1, s2 = self.get_store_from_ram(store_name), self.get_store_from_db(store_name)
        return s1 is None and s2 is None or \
            s1 is not None and s2 is not None and s1.name == s2.name and set(s1.purchase_history) == set(
                s2.purchase_history)

    def get_appointment_from_ram(self, appointee, store_name) -> Appointment | None:
        return self.get_appointment_of(appointee, store_name)

    def get_appointment_from_db(self, appointee, store_name) -> Appointment | None:
        return Appointment.load_appointment(appointee, store_name)

    def verify_appointment_integrity(self, appointee, store_name) -> bool:
        a1, a2 = self.get_appointment_from_ram(appointee, store_name), self.get_appointment_from_db(appointee,
                                                                                                    store_name)
        return a1 is None and a2 is None or \
            a1.store_name == a2.store_name and a1.appointee == a2.appointee and a1.appointed_by == a2.appointed_by and a1.permissions == a2.permissions

    def get_product_from_ram(self, store_name, product_name) -> Product | None:
        store = self.verify_registered_store(self.get_product_from_ram.__qualname__, store_name).result
        if store is not None:
            return store.find(product_name)
        return None

    def get_product_from_db(self, store_name, product_name) -> Product | None:
        return Product.load_product(product_name, store_name)

    def verify_product_integrity(self, store_name, product_name) -> bool:
        p1, p2 = self.get_product_from_ram(store_name, product_name), self.get_product_from_db(store_name, product_name)
        return p1 is None and p2 is None or \
            p1 is not None and p2 is not None and p1.name == p2.name and p1.store_name == p2.store_name and \
            p1.price == p2.price and p1.category == p2.category and p1.quantity == p2.quantity and set(
                p1.keywords) == set(p2.keywords)

    def get_cart_item_from_ram(self, product_name, username, store_name) -> Item | None:
        user = self.verify_registered_user(self.get_cart_item_from_ram.__qualname__, username).result
        if user is not None:
            return user.cart.find_item(product_name, store_name)
        return None

    def get_cart_item_from_db(self, product_name, username, store_name) -> Item | None:
        return Item.load_item(product_name, username, store_name)

    def verify_item_integrity(self, product_name, username, store_name) -> bool:
        i1, i2 = self.get_cart_item_from_ram(product_name, username, store_name), self.get_cart_item_from_db(
            product_name, username, store_name)
        return i1 is None and i2 is None or \
            i1 is not None and i2 is not None and i1.username == i2.username and i1.store_name == i2.store_name and \
            i1.product_name == i2.product_name and i1.quantity == i2.quantity and i1.price == i2.price and \
            i1.discount_price == i2.discount_price

    '''
        End of Validation methods
    '''

    def get_approval_lists_for_store(self, session_id: int, store_name) -> Response:
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.get_approval_lists_for_store.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.get_approval_lists_for_store.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.get_approval_lists_for_store.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.AppointOwner not in perms:
            return report_error(self.get_approval_lists_for_store.__qualname__,
                                f"{actor.username} has no permission to approve things")

        ret_dict = {}
        if self.approval_list.get(store_name) is None:
            ret_dict["owners"] = {}
        else:
            store_dict = self.approval_list.get(store_name)
            ret_dict["owners"] = {}
            for person in store_dict.get_all_keys():
                ret_dict["owners"][person] = store_dict.get(person).left_to_approve()

        bids_dict = {}
        for p in store.products_with_bid_purchase_policy.keys():
            bid = store.products_with_bid_purchase_policy.get(p)
            bids_dict[p] = {}
            bids_dict[p]["price"] = bid.get_cur_bid()
            bids_dict[p]["to_approve"] = bid.approval.left_to_approve()
        ret_dict["bids"] = bids_dict

        return ret_dict

    def is_admin(self, session_id: int):
        return self.get_active_user(session_id).is_admin

    def set_admin_permissions(self):
        all_active_stores = self.stores.get_all_values()
        for store in all_active_stores:
            self.set_permissions_of("Kfir", store.name, Permission.RetrievePurchaseHistory, "ADD")

    def get_bid_products(self, session_id: int, store_name: str) -> Response[dict | bool]:
        response = self.verify_registered_store(self.get_store.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            bids_response = store.get_bid_products()
            r = report_info(self.get_store.__qualname__,
                            f'Return store \'{store_name}\' bids to {actor}\n{bids_response.result.__str__()}')
            bids_response.description = r.description
            return bids_response
        return response
