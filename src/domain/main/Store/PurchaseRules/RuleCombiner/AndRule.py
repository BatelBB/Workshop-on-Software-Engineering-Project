from src.domain.main.Store.PurchaseRules.RuleCombiner.IRuleCombiner import IRuleCombiner
from src.domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from domain.main.User.Basket import Basket
from src.domain.main.Utils.Logger import report
from src.domain.main.Utils.Response import Response


class AndRule(IRuleCombiner):

    def __init__(self, r1: SimpleRule, r2: SimpleRule):
        super().__init__(r1, r2)

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        con1 = self.rule1.enforce_rule(basket)
        con2 = self.rule2.enforce_rule(basket)

        if not con1.success:
            return con1
        elif not con2.success:
            return con2
        return report("and rule good -> Kfir is happy" ,True)