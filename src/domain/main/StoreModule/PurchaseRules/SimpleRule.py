from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class SimpleRule(IRule, Base):
    __tablename__ = 'simple_rules'
    __table_args__ = {'extend_existing': True}
    rule_id = Column("rule_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    product_name = Column("product_name", String, primary_key=True)
    gle = Column("gle", String, primary_key=True)
    num = Column("num", Integer, primary_key=True)

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
                    item.rule_msg = self.__str__()
                    return report_error("enforce_rule", f"invalid basket: {self.__str__()}")

        if self.gle == ">":         # incase the item is not in the cart
            return report_error("enforce_rule", f"invalid basket: {self.__str__()}")

        return Response(True, "good")

    def __str__(self):
        return f'rule: {self.product_name} quantity {self.gle} {self.num}'

    def add_to_db(self):
        SimpleRule.add_record(self)

    def delete_from_db(self):
        SimpleRule.delete_record(self.rule_id, self.store_name)

    @staticmethod
    def create_instance_from_db_query(r):
        rule_id, store_name, product_name, gle, num = r.rule_id, r.store_name, r.product_name, r.gle, r.num
        rule = SimpleRule(product_name, gle, num)
        rule.set_db_info(store_name, rule_id)
        return rule

    @staticmethod
    def load_all_simple_rules():
        out = {}
        for r in DAL.load_all(SimpleRule, SimpleRule.create_instance_from_db_query):
            out[r.rule_id] = r
        return out

    @staticmethod
    def clear_db():
        DAL.clear(SimpleRule)

    @staticmethod
    def add_record(rule):
        DAL.add(rule)

    @staticmethod
    def delete_record(rule_id, store_name):
        DAL.delete(SimpleRule, lambda r: ((r.rule_id == rule_id) and (r.store_name == store_name)))