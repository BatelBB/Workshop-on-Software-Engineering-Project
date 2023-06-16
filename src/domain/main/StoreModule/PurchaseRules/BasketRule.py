from sqlalchemy import Column, Float, String, Integer

from domain.main.Utils import Base_db
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class BasketRule(IRule, Base_db.Base):
    __tablename__ = 'basket_rules'
    __table_args__ = {'extend_existing': True}
    id = Column("id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    min_price = Column("min_price", Float, primary_key=True)

    def __init__(self, min_price: float):
        super().__init__()
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