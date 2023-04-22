from dev.src.main.User.Role.Member import Member
from dev.src.main.Utils.Response import Response


class StoreOwner(Member):
    from dev.src.main.User.User import User
    def __init__(self, context: User, store_name: str, founder: bool):
        super().__init__(context)
        self.context.appointees.update({store_name: []})
        if founder:
            self.context.founded_stores.append(store_name)
        self.context.owned_stores.append(store_name)

    def __str__(self):
        return f'StoreOwner {self.context.username}'

    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

    def is_allowed_to_appoint_owner(self, store_name: str, new_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            self.context.appointees[store_name].append(new_name)
            return Response(True)
        return Response(False)

    def is_allowed_to_appoint_manager(self, store_name: str, new_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            self.context.appointees[store_name].append(new_name)
            return Response(True)
        return Response(False)

    def is_allowed_to_change_permissions(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

    def is_allowed_to_view_store_personal(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

    def is_allowed_to_get_store_purchase_history(self, store_name: str) -> Response[bool]:
        if store_name in self.context.owned_stores:
            return Response(True)
        return Response(False)

