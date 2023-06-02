from domain.main.Store.PurchaseRules.BasketRule import BasketRule
from src.domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.Store.PurchaseRules.RuleCombiner.AndRule import AndRule
from src.domain.main.Store.PurchaseRules.RuleCombiner.ConditioningRule import ConditioningRule
from src.domain.main.Store.PurchaseRules.RuleCombiner.OrRule import OrRule
from src.domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response

rule_types: dict = {"and": (lambda x, y: AndRule(x, y)),
                    "or": (lambda x, y: OrRule(x, y)),
                    "cond": (lambda x, y: ConditioningRule(x, y))}


def make_simple_rule(p_name: str, gle: str, amount: int) -> Response:
    return report("made simple rule", SimpleRule(p_name, gle, amount))


def make_complex_rule(p1: str, gle1: str, amount1: int, p2: str, gle2: str, amount2: int, rule_type: str) -> Response:
    r1 = make_simple_rule(p1, gle1, amount1).result
    r2 = make_simple_rule(p2, gle2, amount2).result

    if rule_type not in rule_types.keys():
        return report_error("make_complex_rule", "invalid ruletype, only: and/or/cond")

    r = rule_types[rule_type](r1, r2)
    return report("make_complex_rule", r)


def make_basket_rule(min_price: float) -> Response:
    return report("made basket rule", BasketRule(min_price))