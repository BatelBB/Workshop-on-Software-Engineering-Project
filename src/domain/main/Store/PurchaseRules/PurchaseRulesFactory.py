from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.Store.PurchaseRules.RuleCombiner.AndRule import AndRule
from domain.main.Store.PurchaseRules.RuleCombiner.ConditioningRule import ConditioningRule
from domain.main.Store.PurchaseRules.RuleCombiner.OrRule import OrRule
from domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from domain.main.Utils.Logger import report_error, report
from domain.main.Utils.Response import Response

rule_types: dict = {"and": (lambda x, y: AndRule(x, y)),
                    "or": (lambda x, y: OrRule(x, y)),
                    "cond": (lambda x, y: ConditioningRule(x, y))}


def make_simple_rule(p_name: str, gle: str, amount: int) -> IRule:
    return SimpleRule(p_name, gle, amount)


def make_complex_rule(p1: str, gle1: str, amount1: int, p2: str, gle2: str, amount2: int, rule_type: str) -> Response:
    r1 = make_simple_rule(p1, gle1, amount1)
    r2 = make_simple_rule(p2, gle2, amount2)

    if rule_type not in rule_types.keys():
        return report_error("make_complex_rule", "invalid ruletype, only: and/or/cond")

    r = rule_types[rule_type](r1, r2)
    return report("make_complex_rule", r)
