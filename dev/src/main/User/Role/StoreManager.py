from dev.src.main.User.Role.Member import Member
from dev.src.main.User.Role.StorePermissions import StorePermissions, get_store_permission_description
from dev.src.main.Utils.Logger import report_error
from dev.src.main.Utils.Response import Response


class StoreManager(Member):
    from dev.src.main.User.User import User
    def __init__(self, context: User, store_name: str):
        super().__init__(context)
        self.context.appointees.update({store_name: []})
        self.permissions: set[StorePermissions] = {StorePermissions.RetrievePurchaseHistory,
                                                   StorePermissions.InteractWithCustomer}

    def __str__(self):
        return f'StoreManager {self.context.username}'

    def report_no_permission(self, calling_method: str, permission: StorePermissions, store_name: str) -> Response[bool]:
        return report_error(calling_method, f'{self} has no permission to {get_store_permission_description(permission)}'
                                            f' on Store \'{store_name}.')
    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(store_name).is_succeed() and StorePermissions.Add in self.permissions \
            else self.report_no_permission(self.is_allowed_add_product.__qualname__, StorePermissions.Add, store_name)

    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(store_name).is_succeed() and StorePermissions.Update in self.permissions \
            else self.report_no_permission(self.is_allowed_update_product.__qualname__, StorePermissions.Add, store_name)

    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(store_name).is_succeed() and StorePermissions.Remove in self.permissions \
            else self.report_no_permission(self.is_allowed_remove_product.__qualname__, StorePermissions.Add, store_name)
