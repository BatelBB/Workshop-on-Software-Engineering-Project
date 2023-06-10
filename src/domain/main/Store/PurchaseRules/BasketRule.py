from src.domain.main.Store.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class BasketRule(IRule):
    min_price: float

    def __init__(self, min_price: float):
        self.min_price = min_price

    # must call with most recent price in basket items!
    def enforce_rule(self, basket: Basket) -> Response[bool]:
        price = 0
        for i in basket.items:
            price += (i.discount_price * i.quantity)
        if price < self.min_price:
            return report_error("enfore basket rule", f"basket price is {price} lower than {self.min_price}")

        return Response(True, "good")

    def __str__(self):
        return f'rule: basket price >= {self.min_price}'