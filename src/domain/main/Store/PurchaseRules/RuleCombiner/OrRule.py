from src.domain.main.Store.PurchaseRules.RuleCombiner.IRuleCombiner import IRuleCombiner
from src.domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from domain.main.User.Basket import Basket
from src.domain.main.Utils.Logger import report, report_error
from src.domain.main.Utils.Response import Response


class OrRule(IRuleCombiner):
    def __init__(self, r1: SimpleRule, r2: SimpleRule):
        super().__init__(r1, r2)

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        con1 = self.rule1.enforce_rule(basket)
        con2 = self.rule2.enforce_rule(basket)

        if (not con1.success) and (not con2.success):
            return report_error("enforce_rule" ,"or law is violated")

        return report("or rule good -> Kfir is happy", True)