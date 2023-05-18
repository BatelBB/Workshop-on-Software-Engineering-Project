from abc import ABC

from src.domain.main.User.Role.Visitor import Visitor
from src.domain.main.Utils.Logger import report_error, report_info
from src.domain.main.Utils.Response import Response


class Member(Visitor, ABC):
    from src.domain.main.User.User import User
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'Member \'{self.context.username}\''

    def login(self, encrypted_password: str) -> Response[bool]:
        return report_error(self.login.__qualname__, f'{self} is already logged in.')

    def register(self) -> Response[bool]:
        return report_error(self.register.__qualname__, f'{self} is already registered.')

    def logout(self) -> Response[bool]:
        if self.context.is_canceled:
            return report_error(self.logout.__qualname__, f'Canceled member \'{self.context.username}\' attempted to logout')
        response = report_info(self.logout.__qualname__, f'{self} is logged out')
        self.context.role = Visitor(self.context)
        self.context.is_logged_in = False
        return response

    def is_logged_in(self) -> bool:
        return not self.context.is_canceled

    def is_member(self) -> bool:
        return not self.context.is_canceled

    def is_admin(self) -> bool:
        return False