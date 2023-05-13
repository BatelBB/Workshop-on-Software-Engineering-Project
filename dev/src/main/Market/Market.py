import random
import sys
from functools import reduce

from dev.src.main.Market.Appointment import Appointment
from dev.src.main.Market.Permissions import Permission, get_default_manager_permissions, get_default_owner_permissions, \
    get_permission_description
from dev.src.main.Store.Product import Product
from dev.src.main.Service.IService import IService
from dev.src.main.Store.Store import Store
from dev.src.main.User.Cart import Cart
from dev.src.main.User.User import User
from dev.src.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from dev.src.main.Utils.Logger import report, Logger, report_error, report_info
from dev.src.main.Utils.Response import Response
from dev.src.main.Utils.Session import Session


class Market(IService):

    # TODO: should be initialized with IPaymentService, IProvisionService
    def __init__(self):
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
        self.appointments: ConcurrentDictionary[str, list[Appointment]] = ConcurrentDictionary()

    def generate_session_identifier(self):
        min: int = 1
        max: int = sys.maxsize
        while True:
            identifier = random.randrange(min, max)
            if self.sessions.get(identifier) is None:
                return identifier

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
        appointments = filter(lambda appointment: appointment.appointed_by == fired_user, self.appointments.get(store_name))
        return list(map(lambda appointment: appointment.appointee, appointments))

    def appointees_at(self, session_identifier: int, store_name: str) -> Response[list[str]]:
        actor = self.get_active_user(session_identifier)
        appointees = self.bfs(actor.username, store_name)
        appointees.remove(actor.username)
        msg = ', '.join(appointees)
        r = report_info(self.appointees_at.__qualname__, f'\'{actor.username}\' appointees at store \'{store_name}\': {msg}')
        return Response(appointees, r.description)

    def add_appointment(self, store_name: str, appointment: Appointment) -> None:
        appointments: list[Appointment] = self.appointments.get(store_name)
        self.appointments.insert(store_name, [appointment]) if appointments is None else appointments.append(appointment)

    def has_permission_at(self, store_name: str, actor: User, permission: Permission) -> bool:
        appointment = self.get_appointment_of(actor.username, store_name)
        return appointment is not None and appointment.is_allowed(permission)

    def is_not_appointed_yet(self, appointee: str, store_name: str) -> bool:
        return self.get_appointment_of(appointee, store_name) is None

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

    def verify_registered_store(self,  calling_method_name: str, store_name: str) -> Response[Store] | Response[bool]:
        store: Store = self.stores.get(store_name)
        return Response(store) if store is not None \
            else report_error(calling_method_name, f'Store \'{store_name}\' is not registered to the market.')

    def verify_registered_user(self,  calling_method_name: str, username: str) -> Response[User] | Response[bool]:
        user: User = self.users.get(username)
        return Response(user) if user is not None \
            else report_error(calling_method_name, f'User \'{username}\' is not registered to the market.')

    def verify_registered_user_and_store(self,  calling_method_name: str, username: str, store_name: str) -> Response[tuple[User, Store]] | Response[bool]:
        response = self.verify_registered_user(calling_method_name, username)
        if response.success:
            user = response.result
            response = self.verify_registered_store(calling_method_name, store_name)
            if response.success:
                store = response.result
                return Response((user, store))
            return response # Unregistered store
        return response # Unregistered user

    def verify_store_contains_product(self, calling_method_name: str, store_name: str, product_name: str) -> Response[Store] | Response[bool]:
        response = self.verify_registered_store(calling_method_name, store_name)
        if response.success:
            store = response.result
            if store.contains(product_name):
                return Response(store)
            else:
                return report_error(calling_method_name, f'Store \'{store_name}\' does not contains Product \'{product_name}\'')
        else:
            return response

    def report_no_permission(self, calling_method: str, actor: User, store: str, permission: Permission):
        return report_error(calling_method, f'\'{actor.username}\' has no permission to {get_permission_description(permission)} at store \'{store}\'')

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
        next_user = self.users.get(username)
        if next_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered')
        response = next_user.login(encrypted_password)
        if response.success:
            current_user = self.get_active_user(session_identifier)
            if current_user.is_member() and current_user != next_user:
                current_user.logout()
            self.sessions.update(session_identifier, next_user)
        return response

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in()

    def logout(self, session_identifier: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
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

    def get_all_stores(self, session_identifier: int) -> Response[list[Store] | bool]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.get_all_stores.__qualname__, f'Return all market stores to {actor}: {self.stores.to_string_keys()}')
        return Response(self.stores.get_all_values(), r.description)

    def get_store(self, session_identifier: int, store_name: str) -> Response[Store | bool]:
        response = self.verify_registered_store(self.get_store.__qualname__, store_name)
        if response.success:
            store = response.result
            actor = self.get_active_user(session_identifier)
            r = report_info(self.get_store.__qualname__, f'Return store \'{store_name}\' to {actor}\n{store.__str__()}')
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
                return report_info(self.add_product.__qualname__, f'\'{actor.username}\' add {quantity} units of {p} to store \'{store_name}\'')
            return self.report_no_permission(self.add_product.__qualname__, actor, store_name, Permission.Add)
        return response

    def remove_product(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        response = self.verify_registered_store(self.remove_product.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Remove):
                return report_info(self.remove_product.__qualname__, f'\'{actor.username}\' remove product \'{product_name}\' from store \'{product_name}\'') if store.remove(product_name)\
                    else report_error(self.remove_product.__qualname__, f'\'{store_name}\' does not contains product \'{product_name}\'')
            return self.report_no_permission(self.remove_product.__qualname__, actor, store_name, Permission.Remove)
        return response

    def update_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        response = self.verify_registered_store(self.update_product_quantity.__qualname__, store_name)
        store = response.result
        if store is not None:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.Update):
                return report_info(self.update_product_quantity.__qualname__, f'\'{actor.username}\' update product \'{product_name}\' at store \'{product_name}\' to {quantity} units') if store.update(product_name, quantity)\
                    else report_error(self.update_product_quantity.__qualname__, f'\'{store_name}\' does not contains product \'{product_name}\'')
            return self.report_no_permission(self.update_product_quantity.__qualname__, actor, store_name, Permission.Remove)
        return response

    def get_amount_of(self, session_identifier: int, product_name: str, store_name: str) -> Response[int]:
        response = self.verify_registered_store(self.get_amount_of.__qualname__, store_name)
        store = response.result
        if store is not None:
            amount = store.amount_of(product_name)
            return Response(amount, f'Amount of \'{product_name}\' at store \'{store_name}\' is {amount}')
        return response

    def appoint(self, session_identifier: int, calling_method: str, store_name: str, appointee_name: str,
                role: Permission, permissions: set[Permission]) -> Response[bool]:
        response = self.verify_registered_user_and_store(calling_method, appointee_name, store_name)
        if response.success:
            appointee, store = response.result
            actor = self.get_active_user(session_identifier)
            if not actor.is_member():
                return report_error(calling_method, f'{appointee} is not allowed to {role.value}.')
            if self.has_permission_at(store_name, actor, role):
                if self.is_not_appointed_yet(appointee_name, store_name):
                    self.add_appointment(store_name, Appointment(appointee_name, actor.username, permissions))
                    return report_info(calling_method, f'{actor} appointed \'{appointee.username}\' to a Store Manager.')
                else:
                    return report_error(calling_method, f'{appointee} is already appointed to a role at store \'{store_name}\'.')
            return self.report_no_permission(calling_method, actor, store_name, role)
        return response # no registered appointee/store

    def get_product_by(self, session_identifier: int, calling_method: str, preidcate) -> Response[list[(str, Product)]]:
        actor = self.get_active_user(session_identifier)
        products = reduce(lambda acc, store: acc + store.get_products_by(preidcate), self.stores.get_all_values(), [])
        msg = reduce(lambda acc, curr: acc + f'Store: \'{curr[0]}\', {curr[1]}\n', products, '')
        r = report_info(calling_method, f'Return filtered products to {actor}:\n{msg}')
        return Response(products, r.description)

    def get_product_by_name(self, session_identifier: int, product_name: str) -> Response[list[(str, Product)]]:
        return self.get_product_by(session_identifier, self.get_product_by_name.__qualname__, lambda p: p.name == product_name)

    def get_product_by_category(self, session_identifier: int, category: str) -> Response[list[(str, Product)]]:
        return self.get_product_by(session_identifier, self.get_product_by_category.__qualname__, lambda p: p.category == category)

    def get_product_by_keywords(self, session_identifier: int, keywords: list[str]) -> Response[list[(str, Product)]]:
        return self.get_product_by(session_identifier, self.get_product_by_keywords.__qualname__, lambda p: len((set(p.keywords) & set(keywords))) > 0)

    def get_product_in_price_range(self, session_identifier: int, min: float, max: float) -> Response[list[(str, Product)]]:
        return self.get_product_by(session_identifier, self.get_product_in_price_range.__qualname__, lambda p: min <= p.price <= max)

    def appoint_manager(self, session_identifier: int, store_name: str, appointee_name: str) -> Response[bool]:
        return self.appoint(session_identifier, self.appoint_manager.__qualname__, store_name, appointee_name,
                            Permission.AppointManager, get_default_manager_permissions())

    def appoint_owner(self, session_identifier: int, store_name: str, appointee_name: str) -> Response[bool]:
        return self.appoint(session_identifier, self.appoint_manager.__qualname__, store_name, appointee_name,
                            Permission.AppointOwner, get_default_owner_permissions())

    def set_permission(self, session_identifier: int, calling_method: str, store: str, appointee: str, permission: Permission, action: {'ADD', 'REMOVE'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if self.is_appointed_by(appointee, actor.username, store):
            self.set_permissions_of(appointee, store, permission, action)
            return report_info(calling_method, f'\'{actor.username}\' {action} permission {get_permission_description(permission)} to \'{appointee}\'')
        return report_error(calling_method, f'\'{appointee}\' is not appointed by \'{actor.username}\'')

    def add_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.set_permission(session_identifier, self.add_permission.__qualname__, store, appointee, permission, 'ADD')

    def remove_permission(self, session_identifier: int, store: str, appointee: str, permission: Permission) -> Response[bool]:
        return self.set_permission(session_identifier, self.remove_permission.__qualname__, store, appointee, permission, 'REMOVE')

    def permissions_of(self, session_identifier: int, store: str, subject: str) -> Response[set[Permission] | bool]:
        appointment = self.get_appointment_of(subject, store)
        actor = self.get_active_user(session_identifier)
        if appointment is not None:
            r = report_info(self.permissions_of.__qualname__, f'Display permission of \'{subject}\' at store \'{store}\' to {actor.username}')
            return Response(appointment.permissions, r.description)
        return report_error(self.permissions_of.__qualname__, f'\'{subject}\' has no role at store \'{store}\'')

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
            return report_info(self.remove_appointment.__qualname__, f'\'{actor.username}\' remove appointment of \'{fired_appointee_successors_msg}\' at store \'{store_name}\'.')
        return report_error(self.remove_appointment.__qualname__, f'\'{fired_appointee}\' is not appointed by {actor.username} at store {store_name}')

    def set_store_activity_status(self, session_identifier: int, calling_method: str, store_name: str, is_active: bool, action: {'CLOSED', 'REOPEN'}) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_member():
            if self.is_founder_of(actor.username, store_name):
                for appointment in self.get_store_appointments(store_name):
                    appointment.is_store_active = is_active # TODO: notify appointee
                return report_info(calling_method, f'Founder \'{actor.username}\' {action} store \'{store_name}\'')
            return report_error(calling_method, f'\'{actor.username}\' is not the founder of store \'{store_name}\'')
        return report_error(calling_method, f'Visitor attempted to {action} store \'{store_name}\'')

    def close_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        return self.set_store_activity_status(session_identifier, self.close_store.__qualname__, store_name, False, 'CLOSED')

    def reopen_store(self, session_identifier: int, store_name: str) -> Response[bool]:
        return self.set_store_activity_status(session_identifier, self.reopen_store.__qualname__, store_name, True, 'REOPEN')

    def staff_to_string(self, appointments: list[Appointment]) -> str:
        out = ''
        i = 1
        for appointment in appointments:
            out += f'{i})\t{appointment}\n'
            i += 1
        return out

    def get_store_staff(self, session_identifier: int, store_name: str) -> Response[list[Appointment] | bool]:
        response = self.verify_registered_store(self.get_store_appointments.__qualname__, store_name)
        if response.success:
            actor = self.get_active_user(session_identifier)
            if self.has_permission_at(store_name, actor, Permission.RetrieveStaffDetails):
                appointments = self.get_store_appointments(store_name)
                r = report_info(self.get_store_appointments.__qualname__, f'Display store \'{store_name}\' staff to {actor}\nStaff\n{self.staff_to_string(appointments)}')
                return Response(appointments, r.description)
            return self.report_no_permission(self.get_store_appointments.__qualname__, actor, store_name, Permission.RetrieveStaffDetails)
        return response

    def add_to_cart(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_registered_store(self.add_to_cart.__qualname__, store_name)
        if response.success:
            store = response.result
            response = store.get_product(product_name)
            if response.success:
                return actor.add_to_cart(store_name, response.result, quantity)
        return response

    def remove_product_from_cart(self, session_identifier: int, store_name: str, product_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.remove_product_from_cart.__qualname__, store_name, product_name)
        return actor.remove_product_from_cart(store_name, product_name) if response.success else response

    def update_cart_product_quantity(self, session_identifier: int, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        response = self.verify_store_contains_product(self.update_cart_product_quantity.__qualname__, store_name, product_name)
        return actor.update_cart_product_quantity(store_name, product_name, quantity) if response.success else response

    def show_cart(self, session_identifier: int) -> Response[Cart]:
        actor = self.get_active_user(session_identifier)
        r = report_info(self.show_cart.__qualname__, f'Cart of \'{actor}\':\n{actor.show_cart()}')
        return Response(actor.cart, r.description)

    def cancel_membership_of(self, session_identifier: int, member_name: str) -> Response[bool]:
        actor = self.get_active_user(session_identifier)
        if actor.is_admin():
            response = self.verify_registered_user(self.cancel_membership_of.__qualname__, member_name)
            if response.success:
                member = response.result
                if not self.has_a_role(member_name):
                    member.is_canceled = True
                    return report_info(self.cancel_membership_of.__qualname__, f'\'{member_name}\' membership is dismissed')
                return report_error(self.cancel_membership_of.__qualname__, f'\'{member_name}\' has a role at the market')
            return response
        return report_error(self.cancel_membership_of.__qualname__, f'\'{actor}\' is not an admin')

    def clear(self) -> None:
        self.__init__()