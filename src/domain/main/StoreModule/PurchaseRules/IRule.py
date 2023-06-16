from abc import ABC, abstractmethod

from domain.main.Utils.Base_db import session_DB
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Response import Response


class IRule:

    def __init__(self):
        self.store_name = None
        self.id = None

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        pass

    def __str__(self):
        pass

    def set_db_info(self, store_name, id):
        self.id = id
        self.store_name = store_name
        return 1

    def add_to_db(self):
        IRule.add_record(self)

    @staticmethod
    def add_record(rule):
        session_DB.add(rule)
        session_DB.commit()