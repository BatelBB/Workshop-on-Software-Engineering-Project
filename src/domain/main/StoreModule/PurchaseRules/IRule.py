from abc import ABC, abstractmethod

from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Response import Response


class IRule():

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
