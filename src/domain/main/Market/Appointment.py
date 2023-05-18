from src.domain.main.Market.Permissions import Permission, get_default_owner_permissions, get_permission_description


class Appointment:
    def __init__(self, appointee: str, appointed_by: str = None, permissions=None):
        if permissions is None:
            permissions = get_default_owner_permissions()
        self.appointee = appointee
        self.appointed_by = appointed_by
        self.permissions = permissions
        self.is_store_active = True

    def __str__(self):
        permissions: str = ', '.join(map(lambda p: str(get_permission_description(p)), self.permissions))
        return f'\'{self.appointee}\', appointed_by: \'{self.appointed_by}\'. Permissions: {permissions}'

    def __eq__(self, other):
        return self.appointee == other.appointee

    def is_allowed(self, required_permission: Permission) -> bool:
        return self.is_store_active and required_permission in self.permissions

