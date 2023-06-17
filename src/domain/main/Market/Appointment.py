from sqlalchemy import Column, String, ForeignKey

from DataLayer.DAL import DAL, Base
from domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Market.Permissions import Permission, get_default_owner_permissions, get_permission_description, \
    serialize_permissions, deserialize_permissions


class Appointment(Base):

    __tablename__ = 'appointments'
    __table_args__ = {'extend_existing': True}
    store_name = Column("store_name", String, ForeignKey('stores.name'), primary_key=True)
    appointee = Column("appointee", String, primary_key=True)
    role = Column("role", String)
    appointed_by = Column("appointed_by", String, nullable=True)
    permissions_str = Column("permissions_str", String)

    def __init__(self, appointee: str, store_name: str, role: {'StoreManager', 'StoreOwner', 'admin'}='StoreOwner', appointed_by: str = None, permissions=None):
        self.appointee = appointee
        self.store_name = store_name
        self.role = role
        self.appointed_by = appointed_by
        if permissions is None:
            permissions = get_default_owner_permissions()
        self.permissions = permissions
        self.is_store_active = True
        self.permissions_str = serialize_permissions(self.permissions)

    @staticmethod
    def create_instance_from_db_query(r):
        return Appointment(r.appointee, r.store_name, r.role, r.appointed_by, deserialize_permissions(r.permissions_str))

    @staticmethod
    def load_appointments_of(store_name):
        return DAL.load_all_by(Appointment, lambda r: r.store_name == store_name, Appointment.create_instance_from_db_query)

    @staticmethod
    def load_all_appointments():
        out = ConcurrentDictionary()
        for r in DAL.load_all(Appointment, Appointment.create_instance_from_db_query):
            out.insert(r.store_name, Appointment.load_appointments_of(r.store_name))
        return out

    @staticmethod
    def clear_db():
        DAL.clear(Appointment)

    @staticmethod
    def delete_record(fired_user, store_name):
        DAL.delete(Appointment, lambda r: r.appointee == fired_user and r.store_name == store_name)

    @staticmethod
    def add_record(appointment):
        DAL.add(appointment)

    @staticmethod
    def load_appointment(appointee, store_name):
        return DAL.load(Appointment, lambda r: r.appointee == appointee and r.store_name == store_name, Appointment.create_instance_from_db_query)

    @staticmethod
    def number_of_records():
        return DAL.size(Appointment)

    def __str__(self):
        permissions: str = ', '.join(map(lambda p: str(get_permission_description(p)), self.permissions))
        return f'{self.role} \'{self.appointee}\', appointed_by: \'{self.appointed_by}\'. Permissions: {permissions}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.appointee == other.appointee

    def is_allowed(self, required_permission: Permission) -> bool:
        return required_permission in self.permissions

    def is_manager(self):
        return self.role == 'StoreManager'

    def is_owner(self):
        return self.role == 'StoreOwner'

    def is_founder(self):
        return self.appointed_by is None

    def add(self, permission):
        self.permissions.add(permission)
        self.permissions_str = serialize_permissions(self.permissions)
        DAL.update(self)

    def remove(self, permission):
        self.permissions.remove(permission)
        self.permissions_str = serialize_permissions(self.permissions)
        DAL.update(self)
