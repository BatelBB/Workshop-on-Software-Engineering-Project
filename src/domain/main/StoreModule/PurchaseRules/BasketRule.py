from sqlalchemy import Column, Integer, String, Float

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class BasketRule(IRule, Base):
    __tablename__ = 'basket_rules'
    __table_args__ = {'extend_existing': True}
    rule_id = Column("rule_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    min_price = Column("num", Float)

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

    def add_to_db(self):
        BasketRule.add_record(self)

    def delete_from_db(self):
        BasketRule.delete_record(self.rule_id, self.store_name)

    @staticmethod
    def create_instance_from_db_query(r):
        rule_id, store_name, min_price = r.rule_id, r.store_name, r.min_price
        rule = BasketRule(min_price)
        rule.set_db_info(store_name, rule_id)
        return rule

    @staticmethod
    def load_all_basket_rules(store_name):
        out = {}
        records = DAL.load_all_by(BasketRule, lambda r: r.store_name == store_name, BasketRule.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.rule_id] = record
        return out

    @staticmethod
    def load_rule_by_id(store_name, rule_id):
        return DAL.load_all_by(BasketRule, lambda r: r.store_name == store_name and r.rule_id == rule_id,
                                 BasketRule.create_instance_from_db_query)

    @staticmethod
    def clear_db():
        DAL.clear(BasketRule)

    @staticmethod
    def add_record(rule):
        DAL.add(rule)

    @staticmethod
    def delete_record(rule_id, store_name):
        DAL.delete(BasketRule, lambda r: ((r.rule_id == rule_id) and (r.store_name == store_name)))