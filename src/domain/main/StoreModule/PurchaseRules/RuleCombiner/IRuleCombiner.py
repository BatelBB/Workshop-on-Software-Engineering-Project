from abc import ABC

from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule


class IRuleCombiner(IRule):
    rule1: IRule
    rule2: IRule

    def __init__(self, r1: IRule, r2: IRule):
        super().__init__()
        self.rule1 = r1
        self.rule2 = r2
        self.id1 = None
        self.id2 = None

    def set_db_info(self, store_name, ident):
        self.store_name = store_name
        self.id = ident
        self.id1 = ident + 1
        self.id2 = ident + 2
        self.rule1.set_db_info(store_name, ident + 1)
        self.rule2.set_db_info(store_name, ident + 2)
        return 3

    def add_to_db(self):
        self.rule1.add_to_db()
        self.rule2.add_to_db()
        IRule.add_record(self)

    def number_of_ids(self):
        return 3