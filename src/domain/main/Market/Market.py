import random
import sys
import threading
from functools import reduce
from typing import Any
import bcrypt
import os
from multipledispatch import dispatch

from domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from domain.main.Store.DiscountPolicy.DIscountsFor.CategoryDiscount import CategoryDiscount
from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.DiscountPolicy.DIscountsFor.ProductDiscount import ProductDiscount
from domain.main.Store.DiscountPolicy.DIscountsFor.StoreDiscount import StoreDiscount
from domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from domain.main.Store.DiscountPolicy.OpenDiscount import OpenDiscount
from domain.main.Store.DiscountPolicy.XorDiscount import XorDiscount
from domain.main.Store.PurchaseRules.IRule import IRule
from src.domain.main.ExternalServices.Payment.PaymentFactory import PaymentFactory
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import provisionService, IProvisionService
from src.domain.main.Market.Appointment import Appointment
from src.domain.main.Market.Permissions import Permission, get_default_manager_permissions, \
    get_default_owner_permissions, \
    get_permission_description
from src.domain.main.Service.IService import IService
from src.domain.main.Store.Product import Product
from src.domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy
from src.domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.Store.PurchasePolicy.LotteryPolicy import LotteryPolicy
from src.domain.main.Store.PurchasePolicy.PurchasePolicyFactory import PurchasePolicyFactory
from src.domain.main.Store.PurchaseRules import PurchaseRulesFactory
from src.domain.main.Store.Store import Store
from src.domain.main.User.Cart import Cart
from src.domain.main.User.Role.Admin import Admin
from src.domain.main.User.User import User
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Logger import Logger, report_error, report_info
from src.domain.main.Utils.Response import Response
from src.domain.main.Utils.Session import Session
from src.domain.main.Store.DiscountPolicy.CondDiscount import CondDiscount


class Market(IService):

    def __init__(self):
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.removed_stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.appointments: ConcurrentDictionary[str, list[Appointment]] = ConcurrentDictionary()
        self.provision_service: IProvisionService = provisionService()
        self.PurchasePolicyFactory: PurchasePolicyFactory = PurchasePolicyFactory()
        self.payment_factory: PaymentFactory = PaymentFactory()
        self.package_counter = 0
        self.appointments_lock = threading.RLock()
        self.init_admin()

    def init_admin(self):
        admin_credentials = ('Kfir', 'Kfir')
        admin_user = User(self, *admin_credentials)
        admin_user.role = Admin(admin_user)
        self.users.insert(admin_credentials[0], admin_user)

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.sessions.get(identifier) is None:
                return identifier

    def enter(self) -> Session:
        session_identifier = self.generate_session_identifier()
        self.sessions.insert(session_identifier, User(self))
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
                i = appointments.index(Appointment(username))
                return appointments[i]
            except Exception:
                return None
        return None

    def remove_appointment_of(self, fired_user: str, store_name: str) -> None:
        self.appointments.get(store_name).remove(Appointment(fired_user))

    def get_appointees_of(self, fired_user: str, store_name: str) -> list[str]:
        appointments = filter(lambda appointment: appointment.appointed_by == fired_user,
                              self.appointments.get(store_name))
        return list(map(lambda appointment: appointment.appointee, appointments))

    def appointees_at(self, session_identifier: int, store_name: str) -> Response[list[str]]:
        actor = self.get_active_user(session_identifier)
        appointees = self.bfs(actor.username, store_name)
        appointees.remove(actor.username)
        msg = ', '.join(appointees)
        r = report_info(self.appointees_at.__qualname__,
                        f'\'{actor.username}\' appointees at store \'{store_name}\': {msg}')
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
                self.appointments.insert(store_name, [appointment]) if appointments is None else appointments.append(
                    appointment)
                return True
            return False

    def is_appointed_by(self, appointee: str, appointed_by: str, store_name: str) -> bool:
        appointment = self.get_appointment_of(appointee, store_name)
        return appointment is not None and appointment.appointed_by == appointed_by

    def set_permissions_of(self, appointee: str, store: str, permission: Permission, action: {'ADD', 'REMOVE'}) -> bool:
        appointment = self.get_appointment_of(appointee, store)
        succeed = appointment is not None
        if succeed:
            appointment.permissions.add(permission) if action == 'ADD' else appointment.permissions.remove(permission)
        return succeed

    def is_founder_of(self, username: str, store_name: str) -> bool:
        return self.get_appointment_of(username, store_name).appointed_by is None

    def is_store_registered(self, store_name: str) -> bool:
        return self.stores.get(store_name) is not None

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
        store: Store = self.stores.get(store_name)
        return Response(store) if store is not None \
            else report_error(calling_method_name, f'Store \'{store_name}\' is not registered to the market.')

    def verify_registered_user(self, calling_method_name: str, username: str) -> Response[User] | Response[bool]:
        user: User = self.users.get(username)
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

    def verify_store_contains_product(self, calling_method_name: str, store_name: str, product_name: str) -> Response[
        Store | bool]:
        response = self.verify_registered_store(calling_method_name, store_name)
        if response.success:
            store = response.result
            return Response(store) if store.contains(product_name) else report_error(calling_method_name,
                                                                                     f'Store \'{store_name}\' does not contains Product \'{product_name}\'')
        return response

    def report_no_permission(self, calling_method: str, actor: User, store: str, permission: Permission):
        return report_error(calling_method,
                            f'\'{actor.username}\' has no permission to {get_permission_description(permission)} at store \'{store}\'')

    def leave(self, session_identifier: int) -> Response[bool]:
        leaving_user = self.sessions.delete(session_identifier)
        leaving_user.logout()
        return report_info(self.leave.__qualname__, f'{leaving_user} left session: {session_identifier}')

    def register(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        password_hash = bcrypt.hashpw(encrypted_password.encode('utf8'), bcrypt.gensalt())
        new_user = User(self, username, password_hash)
        registered_user_with_param_username = self.users.insert(username, new_user)
        if registered_user_with_param_username is None:
            return new_user.register()
        else:
            return report_error(self.register.__qualname__, f'Username: \'{username}\' is occupied')

    def is_registered(self, username: str) -> bool:
        return self.users.get(username) is not None

    def login(self, session_identifier: int, username: str, encrypted_password: str) -> Response[bool]:
        next_user = self.users.get(username)
        if next_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered')
        response = next_user.login(encrypted_password.encode('utf8'))
        current_user = self.get_active_user(session_identifier)
        if current_user.is_logged_in and current_user != next_user:
            current_user.logout()
        self.sessions.update(session_identifier, next_user)
        return response

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        self.sessions.insert(session_identifier, User(self))
        return actor.logout()

    def open_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        store: Store = Store(store_name)
        registered_store_with_same_name = self.stores.insert(store_name, store)
        if registered_store_with_same_name is None:
            if actor.is_member():
                self.add_appointment(store_name, Appointment(actor.username))
                return report_info(self.open_store.__qualname__, f'{actor} opened store \'{store_name}\'.')
            else:
                self.stores.delete(store_name)
                return report_error(self.open_store.__qualname__, f'{actor} is not allowed to open a store.')
        return report_error(self.open_store.__qualname__, f'Store name \'{store_name}\' is occupied.')

    def remove_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        store: Store = Store(store_name)
        if store is not None:
            if actor.is_member():
                self.stores.delete(store_name)
                self.removed_stores.insert(store_name, store)
                return report_info(self.remove_store.__qualname__, f'{actor} removed store {store_name}')
            else:
                return report_error(self.remove_store.__qualname__, f'{actor} is not allowed to remove a store')
        return report_error(self.remove_store.__qualname__, f'store {store_name} doesn\'t exist and can\'t be removed')


    def get_all_stores(self, session_identifier: int) -> Response[list[Store] | bool]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.get_all_stores.__qualname__,
                        f'Return all market stores to {actor}: {self.stores.to_string_keys()}')
        return Response(self.stores.get_all_values(), r.description)

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
            if self.has_permission_at(store_name, actor, Permission.Add):
                p = Product(product_name, category, price, keywords)
                store.add(p, quantity)
                return report_info(self.add_product.__qualname__,
                                   f'\'{actor.username}\' add {quantity} units of {p} to store \'{store_name}\'')
            return self.report_no_permission(self.add_product.__qualname__, actor, store_name, Permission.Add)
        return response

    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Remove):
                return report_info(self.remove_product.__qualname__,
                                   f'\'{actor.username}\' remove product \'{product_name}\' from store \'{product_name}\'') if store.remove(
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
            if self.has_permission_at(store_name, actor, Permission.Update):
                return report_info(self.update_product_quantity.__qualname__,
                                   f'\'{actor.username}\' update product \'{product_name}\' at store \'{product_name}\' to {quantity} units') if store.update(
                    product_name, quantity) \
                    else report_error(self.update_product_quantity.__qualname__,
                                      f'\'{store_name}\' does not contains product \'{product_name}\'')
            return self.report_no_permission(self.update_product_quantity.__qualname__, actor, store_name,
                                             Permission.Remove)
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
                role: {'Store Manager', 'Store Owner'}) -> Response[bool]:
        response = self.verify_registered_user_and_store(calling_method, appointee_name, store_name)
        if response.success:
            appointee, store = response.result
            actor = self.get_active_user(session_identifier)
            if not actor.is_member():
                return report_error(calling_method, f'{appointee} is not allowed to {required_permission.value}.')
            if self.has_permission_at(store_name, actor, required_permission):
                if self.add_appointment(store_name, Appointment(appointee_name, actor.username, permissions)):
                    return report_info(calling_method, f'{actor} appointed \'{appointee.username}\' to a {role}.')
                else:
                    return report_error(calling_method,
                                        f'{appointee} is already appointed to a role at store \'{store_name}\'.')
            return self.report_no_permission(calling_method, actor, store_name, required_permission)
        return response  # no registered appointee/store

    def get_product_by(self, session_identifier: int, calling_method: str, preidcate) -> Response[
        list[dict[str, dict]]]:
        actor = self.get_active_user(session_identifier)
        stores = self.stores.get_all_values()
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
                            Permission.AppointManager, get_default_manager_permissions(), role='Store Manager')

    def appoint_owner(self, session_identifier: int, appointee_name: str, store_name: str) -> Response[bool]:
        return self.appoint(session_identifier, self.appoint_owner.__qualname__, store_name, appointee_name,
                            Permission.AppointOwner, get_default_owner_permissions(), role='Store Owner')

    def set_permission(self, session_identifier: int, calling_method: str, store: str, appointee: str,
                       permission: Permission, action: {'ADD', 'REMOVE'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if self.is_appointed_by(appointee, actor.username, store):
            self.set_permissions_of(appointee, store, permission, action)
            return report_info(calling_method,
                               f'\'{actor.username}\' {action} permission {get_permission_description(permission)} to \'{appointee}\'')
        return report_error(calling_method, f'\'{appointee}\' is not appointed by \'{actor.username}\'')

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
                            f'Display permission of \'{subject}\' at store \'{store}\' to {actor.username}')
            return Response(appointment.permissions, r.description)
        return report_error(self.permissions_of.__qualname__, f'\'{subject}\' has no role at store \'{store}\'')

    def get_admin_permissions(self) -> Response[set[Permission] | bool]:
        r = report_info(self.permissions_of.__qualname__,
                        f'Display permission of admin')
        return Response(get_default_owner_permissions(), r.description)

    '''
        Store appointments creates a tree
        We iterate over the subtree of root in a breath-first-manner to aggregate all its successive appointees
    '''

    def bfs(self, root: str, store_name: str) -> list[str]:
        successors: list[str] = list()
        queue: list[str] = list()
        queue.append(root)
        while len(queue) > 0:
            parent = queue.pop()
            successors.append(parent)
            for successor in self.get_appointees_of(parent, store_name):
                queue.append(successor)
        return successors

    def remove_appointment(self, session_identifier: int, fired_appointee: str, store_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if self.is_appointed_by(fired_appointee, actor.username, store_name):
            fired_appointee_successors = self.bfs(fired_appointee, store_name)
            fired_appointee_successors_msg = ', '.join(fired_appointee_successors)
            [self.remove_appointment_of(fired, store_name) for fired in fired_appointee_successors]
            return report_info(self.remove_appointment.__qualname__,
                               f'\'{actor.username}\' remove appointment of \'{fired_appointee_successors_msg}\' at store \'{store_name}\'.')
        return report_error(self.remove_appointment.__qualname__,
                            f'\'{fired_appointee}\' is not appointed by {actor.username} at store {store_name}')

    def set_store_activity_status(self, session_identifier: int, calling_method: str, store_name: str, is_active: bool,
                                  action: {'CLOSED', 'REOPEN'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_member():
            if self.is_founder_of(actor.username, store_name):
                for appointment in self.get_store_appointments(store_name):
                    appointment.is_store_active = is_active  # TODO: notify appointee
                return report_info(calling_method, f'Founder \'{actor.username}\' {action} store \'{store_name}\'')
            return report_error(calling_method, f'\'{actor.username}\' is not the founder of store \'{store_name}\'')
        return report_error(calling_method, f'Visitor attempted to {action} store \'{store_name}\'')

    def close_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        return self.set_store_activity_status(session_identifier, self.close_store.__qualname__, store_name, False,
                                              'CLOSED')

    def reopen_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        return self.set_store_activity_status(session_identifier, self.reopen_store.__qualname__, store_name, True,
                                              'REOPEN')

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
        response = self.verify_store_contains_product(self.add_to_cart.__qualname__, store_name, product)
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
                                                      product_name)
        return actor.remove_product_from_cart(store_name, product_name) if response.success else response

    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str,
                                     quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.update_cart_product_quantity.__qualname__, store_name,
                                                      product_name)
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
                                    f'\'{store_name}\' does not contains product \'{product_old_name}\'')
            return self.report_no_permission(self.change_product_name.__qualname__, actor, store_name,
                                             Permission.Update)
        return response

    def change_product_price(self, session_identifier: int, store_name: str, product_old_price: float,
                             product_new_price: float) -> Response[bool]:
        response = self.verify_registered_store(self.change_product_price.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Update):
                store.change_product_price(product_old_price, product_new_price)
                return report_info(self.change_product_price.__qualname__,
                                   f'Product of price {product_old_price} changed to \'{product_new_price}\' at store \'{store_name}\' by {actor}')
            return self.report_no_permission(self.change_product_price.__qualname__, actor, store_name,
                                             Permission.Update)
        return response

    def change_product_category(self, session_identifier: int, store_name: str, product_name: str, category: str) -> Response[bool]:
        response = self.verify_registered_store(self.change_product_category.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Update):
                store.change_product_category(product_name, category)
                return report_info(self.change_product_category.__qualname__,
                                   f'Product {product_name} category changed to \'{category}\' at store \'{store_name}\' by {actor}')
            return self.report_no_permission(self.change_product_category.__qualname__, actor, store_name,
                                             Permission.Update)
        return response

    def show_cart(self, session_identifier: int) -> Response[dict | bool]:
        actor = self.get_active_user(session_identifier)
        r = actor.show_cart()
        report_info(self.show_cart.__qualname__, r.description)
        return r

    def get_cart(self, session_identifier: int) -> Response[Cart]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.get_cart.__qualname__, f'Cart of {actor}\n{actor.cart}')
        return Response(actor.cart, r.description)

    def cancel_membership_of(self, session_identifier: int, member_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_admin():
            response = self.verify_registered_user(self.cancel_membership_of.__qualname__, member_name)
            if response.success:
                member = response.result
                if not self.has_a_role(member_name):
                    member.is_canceled = True
                    return report_info(self.cancel_membership_of.__qualname__,
                                       f'\'{member_name}\' membership is dismissed')
                return report_error(self.cancel_membership_of.__qualname__,
                                    f'\'{member_name}\' has a role at the market')
            return response
        return report_error(self.cancel_membership_of.__qualname__, f'\'{actor}\' is not an admin')

    def clear(self) -> None:
        self.__init__()

    def pay(self, price: int, payment_type: str, payment_details: list[str], holder: str, user_id: int):
        if price > 0:
            try:
                payment_strategy: IPaymentService = self.payment_factory.getPaymentService(payment_type)
                info_res = payment_strategy.set_information(payment_details, holder, user_id)
                if info_res.success:
                    payment_res = payment_strategy.pay(price)
                    if not payment_res:
                        report_error(self.pay.__qualname__, f'paying failed')
                    else:
                        return payment_strategy
                else:
                    report_error(self.pay.__qualname__, f'setting payment information failed {info_res}')
            except Exception:
                report_error(self.pay.__qualname__, "failed to get payment service")

    def add_to_purchase_history(self, baskets: dict[str, Any]) -> None:
        for store_name, basket in baskets.items():
            self.stores.get(store_name).add_to_purchase_history(basket)

    def update_user_cart_after_purchase(self, user: User, store_names: list) -> None:
        for store_name in store_names:
            user.empty_basket(store_name)

    def purchase_shopping_cart(self, session_identifier: int, payment_method: str, payment_details: list[str],
                               address: str, postal_code: str, city: str, country: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        holder = actor.username
        user_id = actor.get_user_id()
        response = actor.verify_cart_not_empty()
        if response.success:
            baskets = actor.get_baskets()
            cart_price = 0
            successful_store_purchases = []

            for store_name, basket in baskets.items():
                response2 = self.verify_registered_store(self.purchase_shopping_cart.__qualname__, store_name)
                if response2.success:
                    store = response2.result
                    res = store.reserve_products(basket)
                    if res:
                        successful_store_purchases.append(store_name)
                        cart_price += store.calculate_basket_price(basket)
                else:
                    return response2.success
            payment_succeeded = self.pay(cart_price, payment_method, payment_details, holder, user_id)
            if payment_succeeded:
                # order delivery
                delivery_service = provisionService()
                delivery_service.set_info(actor.username, 0, address, postal_code, city, country)
                if not delivery_service.getDelivery():
                    payment_succeeded.refund(cart_price)
                    return report_error(self.purchase_shopping_cart.__qualname__, 'failed delivery')
                self.add_to_purchase_history(baskets)
                self.update_user_cart_after_purchase(actor, successful_store_purchases)
                return Response(True)
            else:
                return report_error(self.purchase_shopping_cart.__qualname__, "payment_succeeded = false")
        else:
            return response

    def get_store_purchase_history(self, session_id: int, store_name: str = "") -> Response[bool]:
        response = self.verify_registered_store(self.get_store_purchase_history.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_id)
            store = response.result
            if self.has_permission_at(store_name, actor, Permission.RetrievePurchaseHistory):
                return report_info(self.get_store_purchase_history.__qualname__,
                                   f'{actor} retrieved store \'{store_name}\' purchase history:\n{store.get_purchase_history()}')
            return self.report_no_permission(self.get_store_purchase_history.__qualname__, actor, store_name,
                                             Permission.RetrievePurchaseHistory)
        return response

    def purchase_with_non_immediate_policy(self, session_identifier: int, store_name: str, product_name: str,
                                           payment_method: str, payment_details: list[str], address: str,
                                           postal_code: str, how_much: float, city: str, country: str):
        response = self.verify_registered_store(self.purchase_with_non_immediate_policy.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            holder = actor.username
            user_id = actor.get_user_id()
            try:
                payment_service = self.payment_factory.getPaymentService(payment_method)
            except Exception:
                report_error(self.purchase_with_non_immediate_policy.__qualname__, f'failed getting payment service')
            payment_service.set_information(payment_details, holder, user_id)
            delivery_service = provisionService()
            delivery_service.set_info(actor.username, 0, address, postal_code, store_name, city, country)
            return store.apply_purchase_policy(payment_service, product_name, delivery_service, how_much)

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
                policy = BidPolicy()
                return store.add_product_to_bid_purchase_policy(product_name, policy, self.get_store_staff(store_name))
            return self.report_no_permission(self.start_bid.__qualname__, actor, store_name, Permission.StartBid)
        return response

    def approve_bid(self, session_id: int, store_name: str, product_name: str, is_approve: bool) -> Response:
        response = self.verify_registered_store(self.approve_bid.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_id)
            if self.has_permission_at(store_name, actor, Permission.ApproveBid):
                return store.approve_bid(actor.username, product_name, is_approve, self.get_store_staff(store_name))
            return self.report_no_permission(self.approve_bid.__qualname__, actor, store_name, Permission.StartBid)
        return response

    def rule_maker(self, rule_type: str, p1_name: str = None, gle1: str = None, amount1: int= None, p2_name: str= None,
                   gle2: str= None, amount2: int= None, min_price: float = None) -> Response[IRule]:
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
                return store.add_purchase_rule(rule)
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
                return store.add_purchase_rule(rule)
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

    def discount_for_factory(self, discount_for_type: str, store, discount_for_name: str = None):
        if discount_for_type == "product":
            return Response(ProductDiscount(store.get_product_obj(discount_for_name).result),
                            f"discount_for {discount_for_type} is made")
        elif discount_for_type == "category":
            return Response(CategoryDiscount(discount_for_name), f"discount_for {discount_for_type} is made")
        elif discount_for_type == "store":
            return Response(StoreDiscount(), f"discount_for {discount_for_type} is made")

        report_error(self.discount_for_factory.__qualname__, f"{discount_for_type} is invalid discount for type")

    def make_simple_discount(self, discount_percent: int, discount_durations: int,
                         discount_for: IDiscountFor, rule: IRule = None) -> Response[IDiscountPolicy]:
        discount = OpenDiscount(discount_percent, discount_for, discount_durations)
        return Response(discount, "made discount")

    ### discount_type = open | cond
    ### discount_for type: product | category | store
    ### cond_type: simple | and | or | basket
    ###
    def add_discount(self, session_id: int, store_name: str, discount_type: str, discount_percent: int,
                     discount_duration: int, discount_for_type: str, discount_for_name: str = None,
                     rule_type=None,
                     discount2_percent=None, discount2_for_type=None, discount2_for_name=None,
                     cond_type: str = None, min_price: float = None,
                     p1_name=None, gle1=None, amount1=None, p2_name=None, gle2=None, amount2=None):
        actor = self.get_active_user(session_id)
        store_res = self.verify_registered_store(self.add_discount.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.add_discount.__qualname__, "invalid store")
        store = store_res.result

        perms = self.permissions_of(session_id, store_name, actor.username)
        if not perms.success:
            return report_error(self.add_discount.__qualname__, "failed to retrieve permissions")
        perms = perms.result

        if Permission.ChangeDiscountPolicy not in perms:
            return report_error(self.add_discount.__qualname__, f"{actor.username} has no permission to add discount")

        dis_res = self.discount_for_factory(discount_for_type, store, discount_for_name)
        if not dis_res.success:
            return dis_res

        discount: IDiscountPolicy
        dis_for = dis_res.result
        dis_res = self.make_simple_discount(discount_percent, discount_duration, dis_for)
        if not dis_res.success:
            return dis_res
        simple_discount1 = dis_res.result
        discount = simple_discount1

        if discount_type == "cond" or discount_type == "xor":
            res = self.rule_maker(rule_type, p1_name, gle1, amount1, p2_name, gle2, amount2, min_price)
            if not res.success:
                return res
            rule: IRule = res.result

        if discount_type == "cond":
            cond_discount = CondDiscount(simple_discount1, rule)
            discount = cond_discount

        if discount_type == "xor":
            dis_res2 = self.discount_for_factory(discount2_for_type, store, discount2_for_name)
            if not dis_res2.success:
                return dis_res2
            simple_discount2 = self.make_simple_discount(discount2_percent, discount_duration, dis_res2.result).result
            discount = XorDiscount(simple_discount1, simple_discount2, rule, discount_duration)

        return store.add_discount_policy(discount)

    def get_store_products_with_discounts(self, session_id: int, store_name: str) -> dict[Product:str]:
        store_res = self.verify_registered_store(self.add_discount.__qualname__, store_name)
        if not store_res.success:
            return report_error(self.add_discount.__qualname__, "invalid store")
        store = store_res.result

        dict = store.get_products_with_discounts()
        return dict