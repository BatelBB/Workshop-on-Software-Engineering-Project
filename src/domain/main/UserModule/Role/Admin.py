from abc import ABC

import bcrypt

from src.domain.main.UserModule.Role.Member import Member
from src.domain.main.Utils.Logger import report_error, report_info
from src.domain.main.Utils.Response import Response


class Admin(Member, ABC):
    from src.domain.main.UserModule.User import User
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'Admin \'{self.context.username}\''

    def is_admin(self) -> bool:
        return True

    def login(self, input_password: str) -> Response[bool]:
        if not bcrypt.checkpw(bytes(input_password, 'utf8'), self.context.encrypted_password):
            return report_error(self.login.__qualname__, f'{self} enter an incorrect password.')
        if not self.context.is_logged_in:
            self.context.is_logged_in = True
            return report_info(self.login.__qualname__, f'{self} is logged in.')
        return report_error(self.login.__qualname__, f'{self} is already logged in')