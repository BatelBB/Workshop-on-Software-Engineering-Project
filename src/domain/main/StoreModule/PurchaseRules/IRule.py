from abc import ABC, abstractmethod

from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Response import Response


class IRule:

    def __init__(self):
        self.store_name = None
        self.rule_id = None

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        pass

    def __str__(self):
        pass

    def set_db_info(self, store_name, rule_id):
        self.rule_id = rule_id
        self.store_name = store_name
        return 1

    def add_to_db(self):
        pass

    def delete_from_db(self):
        pass

    def number_of_ids(self):
        return 1