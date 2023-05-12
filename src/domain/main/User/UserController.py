from src.domain.main.Utils.Logger import report_error
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Response import Response
from src.domain.main.User.User import User


class UserController:

    def __init__(self):
        self.sessions: ConcurrentDictionary[int, User] = ConcurrentDictionary()
        self.users: ConcurrentDictionary[str, User] = ConcurrentDictionary()
    def get_active_user(self, session_identifier: int) -> User | None:
        s = self.sessions.get(session_identifier)
        return s

    def leave(self, session_identifier: int) -> Response[bool]:
        leaving_user = self.sessions.delete(session_identifier)
        return leaving_user.leave(session_identifier)

    def register(self, new_user: User, username: str ) -> Response[bool]:
        registered_user_with_param_username = self.users.insert(username, new_user)
        if registered_user_with_param_username is None:
            return new_user.register()
        else:
            return report_error(self.register.__qualname__, f'Username: {username} is occupied')

    def login(self, session_identifier: int, username: str, password: str):
        registered_user = self.users.get(username)
        if registered_user is None:
            return report_error(self.login.__qualname__, f'Username: \'{username}\' is not registered)')
        else:
            response = registered_user.login(password)
            if response.success:
                self.sessions.update(session_identifier, registered_user)
            return response
    def is_registered(self, username: str) -> bool:
        return self.users.get(username) is not None

    def is_logged_in(self, username: str) -> bool:
        return self.is_registered(username) and self.users.get(username).is_logged_in()

    def get_registered_user(self, name: str) -> Response[User] | Response[bool]:
        if self.users.get(name) is not None:
            return Response(self.users.get(name))
        return Response(False)


    def appoint_store_owner(self, session_id: int, new_owner_name: str, store_name: str):
        user_res = self.get_registered_user(new_owner_name)
        if not user_res.success:
            return user_res
        user = user_res.result
        actor = self.get_active_user(session_id)
        response = actor.is_allowed_to_appoint_owner(store_name, new_owner_name)
        if not response.success:
            return response
        return user.make_me_owner(store_name)

    def appoint_store_manager(self, session_id: int, new_manager_name: str, store_name: str):
        user_res = self.get_registered_user(new_manager_name)
        if not user_res.success:
            return user_res
        user = user_res.result
        actor = self.get_active_user(session_id)
        response = actor.is_allowed_to_appoint_manager(store_name, new_manager_name)
        if not response.success:
            return response
        return user.make_me_owner(store_name)

    def stock_permissions(self, session_id: int, receiving_user_name: str, store_name: str, give_or_take: bool):
        actor = self.get_active_user(session_id)
        res = actor.is_allowed_to_change_permissions(store_name)
        if not res.success:
            return res

        receiving_user = self.get_registered_user(receiving_user_name)
        if not receiving_user.success:
            return receiving_user
        receiving_user = receiving_user.result

        return receiving_user.set_stock_permissions(store_name, give_or_take)

    def personal_permissions(self, session_id: int, receiving_user_name: str, store_name: str, give_or_take: bool):
        actor = self.get_active_user(session_id)
        res = actor.is_allowed_to_change_permissions(store_name)
        if not res.success:
            return res
        receiving_user = self.get_registered_user(receiving_user_name)
        if not receiving_user.success:
            return receiving_user
        receiving_user = receiving_user.result
        return receiving_user.set_personal_permissions(store_name, give_or_take)

    def fire_employee(self, session_id: int, store_name: str, employee_name: str):
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
