from src.domain.main.User.Role.Member import Member
from src.domain.main.User.User import User
from src.domain.main.Utils.Logger import report_error, report_info
from src.domain.main.Utils.Response import Response


class SystemAdmin(Member):
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'SystemAdmin {self.context.username}'

    def is_allowed_to_get_store_purchase_history(self, store_name: str) -> Response[bool]:
        return Response(True)

    def is_allowed_to_shutdown_market(self) -> Response[bool]:
        return Response(True)

    def login(self, encrypted_password: str):
        if encrypted_password != self.context.encrypted_password:
            return report_error(self.login.__qualname__, f'{self} enter an incorrect password.')
        return report_info(self.login.__qualname__, f'{self.context.username} is logged in.')

    def is_allowed_to_view_entrance_history(self):
        return Response(True)