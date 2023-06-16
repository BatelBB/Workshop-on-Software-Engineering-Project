from sqlalchemy import Column, String, Float, Integer

from domain.main.Utils import Base_db
from src.domain.main.Utils.Base_db import session_DB
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class SimpleRule(IRule, Base_db.Base):
    __tablename__ = 'simple_rules'
    __table_args__ = {'extend_existing': True}
    id = Column("id", Float, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    product_name = Column("product_name", String, primary_key=True)
    gle = Column("gle", String, primary_key=True)
    num = Column("num", Integer, primary_key=True)

    def __init__(self, product_name: str, gle: str, num: int):
        super().__init__()
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
                    item.rule_msg = self.__str__()
                    return report_error("enforce_rule", f"invalid basket: {self.__str__()}")

        if self.gle == ">":         # incase the item is not in the cart
            return report_error("enforce_rule", f"invalid basket: {self.__str__()}")

        return Response(True, "good")

    def __str__(self):
        return f'rule: {self.product_name} quantity {self.gle} {self.num}'


