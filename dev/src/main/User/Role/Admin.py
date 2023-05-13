from abc import ABC

from dev.src.main.User.Role.Member import Member


class Admin(Member, ABC):
    from dev.src.main.User.User import User
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'Admin \'{self.context}\''

    def is_admin(self) -> bool:
        return True