from src.domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.User.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class SimpleRule(IRule):
    product_name: str
    gle: str
    num: int
    funcs: dict

    def __init__(self, product_name: str, gle: str, num: int):
        self.product_name = product_name
        self.num = num
        if gle == ">" or gle == "<" or gle == "=":
            self.gle = gle
        else:
            report_error("Rule init:", "gle must be > < or =")
        self.funcs = {">": (lambda x, y: x > y),
                      "<": (lambda x, y: x < y),
                      "=": (lambda x, y: x == y)}

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        for item in basket.items:
            if item.product_name == self.product_name:
                if self.funcs[self.gle](item.quantity, self.num):
                    return report("law is kept Kfir is happy!", True)
                else:
                    return report_error("enforce_rule", "justice is served!")

        if self.gle == ">":         # incase the item is not in the cart
            return report_error("enforce_rule", "justice is served!")

        return Response(True, "good")

    def __str__(self):
        return f'rule: {self.product_name} quantity {self.gle} {self.num}'