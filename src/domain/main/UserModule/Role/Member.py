from abc import ABC

from src.domain.main.UserModule.Role.Visitor import Visitor
from src.domain.main.Utils.Logger import report_error, report_info
from src.domain.main.Utils.Response import Response


class Member(Visitor, ABC):
    def __init__(self, context):
        super().__init__(context)

    def __str__(self):
        return f'Member \'{self.context.username}\''

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