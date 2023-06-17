from abc import ABC

from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule


class IRuleCombiner(IRule):
    rule1: SimpleRule
    rule2: SimpleRule

    def __init__(self, r1: IRule, r2: IRule):
        super().__init__()
        self.rule1 = r1
        self.rule2 = r2
        self.rule_id1 = None
        self.rule_id2 = None

    def number_of_ids(self):
        return 3

    def set_db_info(self, store_name, rule_id):
        self.rule_id = rule_id
        self.store_name = store_name
        self.rule_id1 = rule_id + 1
        self.rule_id2 = rule_id + 2
        if self.rule1 is not None:
            self.rule1.set_db_info(store_name, rule_id+1)
            self.rule2.set_db_info(store_name, rule_id+2)
        return 3

    def add_to_db(self):
        self.rule1.add_to_db()
        self.rule2.add_to_db()

    def delete_from_db(self):
        self.rule1.delete_from_db()
        self.rule2.delete_from_db()