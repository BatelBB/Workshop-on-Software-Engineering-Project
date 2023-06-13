import threading

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Column, String, ForeignKey

from src.domain.main.Utils import Base_db
from src.domain.main.Utils.Base_db import session_DB
from src.domain.main.Market.Permissions import Permission, get_default_owner_permissions, get_permission_description, \
    serialize_permissions, deserialize_permissions


class Appointment(Base_db.Base):

    __tablename__ = 'appointments'
    __table_args__ = {'extend_existing': True}
    store_name = Column("store_name", String, ForeignKey('stores.name'), primary_key=True)
    appointee = Column("appointee", String, primary_key=True)
    role = Column("role", String)
    appointed_by = Column("appointed_by", String, nullable=True)
    permissions_str = Column("permissions_str", String)

    def __init__(self, appointee: str, store_name: str, role: {'StoreManager', 'StoreOwner'}='StoreOwner', appointed_by: str = None, permissions=None):
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
    def load_appointments_of(store_name):
        appointments = []
        q = session_DB.query(Appointment).filter(Appointment.store_name == store_name).all()
        exist = len(q) > 0
        if exist:
            for r in q:
                appointments.append(Appointment(r.appointee, r.store_name, r.role, r.appointed_by, deserialize_permissions(r.permissions_str)))
            return appointments
        return None

    @staticmethod
    def clear_db():
        session_DB.query(Appointment).delete()
        session_DB.commit()

    @staticmethod
    def delete_record(fired_user, store_name):
        q = session_DB.query(Appointment).filter(Appointment.appointee == fired_user, Appointment.store_name == store_name).all()
        is_exists = len(q) > 0
        if is_exists:
            for r in q:
                session_DB.delete(r)
            session_DB.commit()

    @staticmethod
    def add_record(appointment):
        session_DB.merge(appointment)
        session_DB.commit()

    def __str__(self):
        permissions: str = ', '.join(map(lambda p: str(get_permission_description(p)), self.permissions))
        return f'{self.role} \'{self.appointee}\', appointed_by: \'{self.appointed_by}\'. Permissions: {permissions}'

    def __repr__(self):
        return self.__str__()
    def __eq__(self, other):
        return self.appointee == other.appointee

    def is_allowed(self, required_permission: Permission) -> bool:
        return self.is_store_active and required_permission in self.permissions

    def is_manager(self):
        return self.role == 'StoreManager'

    def is_owner(self):
        return self.role == 'StoreOwner'

    def is_founder(self):
        return self.appointed_by is None

    def add(self, permission):
        self.permissions.add(permission)
        r = session_DB.query(Appointment).filter(Appointment.appointee == self.appointee, Appointment.store_name == self.store_name).first()
        r.permissions_str = serialize_permissions(self.permissions)
        session_DB.commit()

    def remove(self, permission):
        self.permissions.remove(permission)
        r = session_DB.query(Appointment).filter(Appointment.appointee == self.appointee, Appointment.store_name == self.store_name).first()
        r.permissions_str = serialize_permissions(self.permissions)
        session_DB.commit()

