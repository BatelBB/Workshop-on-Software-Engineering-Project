from dev.src.main.User.Role.Member import Member
from dev.src.main.User.Role.StorePermissions import StorePermissions, get_store_permission_description
from dev.src.main.Utils.Logger import report_error, report_info
from dev.src.main.Utils.Response import Response


class StoreManager(Member):
    from dev.src.main.User.User import User
    def __init__(self, context: User, store_name: str):
        super().__init__(context)
        self.context.appointees.update({store_name: []})
        self.permissions: set[StorePermissions] = {StorePermissions.Add,
                                                   StorePermissions.Update,
                                                   StorePermissions.Remove}

    def __str__(self):
        return f'StoreManager {self.context.username}'

    def report_no_permission(self, calling_method: str, permission: StorePermissions, store_name: str) -> Response[
        bool]:
        return report_error(calling_method,
                            f'{self} has no permission to {get_store_permission_description(permission)}'
                            f' on Store \'{store_name}.')

    def is_allowed_add_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(store_name).success and StorePermissions.Add in self.permissions \
            else self.report_no_permission(self.is_allowed_add_product.__qualname__, StorePermissions.Add, store_name)

    def is_allowed_update_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(
            store_name).success and StorePermissions.Update in self.permissions \
            else self.report_no_permission(self.is_allowed_update_product.__qualname__, StorePermissions.Add,
                                           store_name)

    def is_allowed_remove_product(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(
            store_name).success and StorePermissions.Remove in self.permissions \
            else self.report_no_permission(self.is_allowed_remove_product.__qualname__, StorePermissions.Add,
                                           store_name)

    def is_allowed_appoint_owner(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(
            store_name).success and StorePermissions.AppointOwner in self.permissions \
            else self.report_no_permission(self.is_allowed_remove_product.__qualname__, StorePermissions.Add,
                                           store_name)

    def is_allowed_appoint_manager(self, store_name: str) -> Response[bool]:
        return Response(True) if self.is_appointed_of(
            store_name).success and StorePermissions.AppointManager in self.permissions \
            else self.report_no_permission(self.is_allowed_remove_product.__qualname__, StorePermissions.Add,
                                           store_name)

    def set_stock_permissions(self, store_name: str, give_or_take: bool) -> Response[bool]:
        if not self.is_appointed_of(store_name):
            return report_error("set_stock_permissions", f'user {self} is not appointed of store {store_name}\n')
        if give_or_take:
            self.permissions.add(StorePermissions.Add)
            self.permissions.add(StorePermissions.Remove)
            self.permissions.add(StorePermissions.Update)
            return report_info("set_stock_permissions", f'user {self} got stock permissions at {store_name}\n')
        else:
            self.permissions.remove(StorePermissions.Add)
            self.permissions.remove(StorePermissions.Remove)
            self.permissions.remove(StorePermissions.Update)
            return report_info("set_stock_permissions", f'user {self} removed stock permissions at {store_name}\n')

    def set_personal_permissions(self, store_name: str, give_or_take: bool) -> Response[bool]:
        if not self.is_appointed_of(store_name):
            return report_error("set_stock_permissions", f'user {self} is not appointed of store {store_name}\n')
        if give_or_take:
            self.permissions.add(StorePermissions.AppointManager)
            self.permissions.add(StorePermissions.RetrieveStaffDetails)
            self.permissions.add(StorePermissions.RetrievePurchaseHistory)
            return report_info("set_stock_permissions", f'user {self} got personal permissions at {store_name}\n')
        else:
            self.permissions.remove(StorePermissions.AppointManager)
            self.permissions.remove(StorePermissions.RetrieveStaffDetails)
            self.permissions.remove(StorePermissions.RetrievePurchaseHistory)
            return report_info("set_stock_permissions", f'user {self} removed personal permissions at {store_name}\n')
