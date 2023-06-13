from abc import ABC

from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule


class IRuleCombiner(IRule, ABC):
    rule1: SimpleRule
    rule2: SimpleRule

    def __init__(self, r1: SimpleRule, r2: SimpleRule):
        self.rule1 = r1
        self.rule2 = r2