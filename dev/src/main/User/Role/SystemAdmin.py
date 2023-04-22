from dev.src.main.User.Role.Member import Member
from dev.src.main.User.User import User
from dev.src.main.Utils.Response import Response


class SystemAdmin(Member):
    def __init__(self, context: User):
        super().__init__(context)

    def __str__(self):
        return f'SystemAdmin {self.context.username}'

    def is_allowed_to_get_store_purchase_history(self) -> Response[bool]:
        return Response(True)

    def is_allowed_to_shutdown_market(self) -> Response[bool]:
        return Response(True)