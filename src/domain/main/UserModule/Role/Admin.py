from abc import ABC

import bcrypt

from src.domain.main.UserModule.Role.Member import Member


class Admin(Member, ABC):
    def __init__(self, context):
        super().__init__(context)

    def login(self, input_password: str) -> bool:
        is_password_matched = bcrypt.checkpw(bytes(input_password, 'utf8'), self.context.encrypted_password)
        if is_password_matched:
            self.context.is_logged_in = True
        return is_password_matched

    def __str__(self):
        return f'Admin \'{self.context.username}\''

    def is_admin(self) -> bool:
        return True