from abc import ABC

from domain.main.Store.PurchaseRules.Rule import Rule
from domain.main.Store.PurchaseRules.SimpleRule import SimpleRule


class IRuleCombiner(Rule, ABC):
    rule1: SimpleRule
    rule2: SimpleRule

    def __init__(self, r1: SimpleRule, r2: SimpleRule):
        self.rule1 = r1
        self.rule2 = r2
