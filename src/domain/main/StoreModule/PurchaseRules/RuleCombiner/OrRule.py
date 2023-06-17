from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.IRuleCombiner import IRuleCombiner
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report, report_error
from src.domain.main.Utils.Response import Response


class OrRule(IRuleCombiner, Base):
    __tablename__ = 'or_rules'
    __table_args__ = {'extend_existing': True}
    rule_id = Column("rule_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    rule_id1 = Column("rule_id1", Integer)
    rule_id2 = Column("rule_id2", Integer)

    def __init__(self, r1: IRule=None, r2: IRule=None):
        super().__init__(r1, r2)

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        con1 = self.rule1.enforce_rule(basket)
        con2 = self.rule2.enforce_rule(basket)

        if (not con1.success) and (not con2.success):
            return report_error("enforce_rule" ,"or law is violated")

        return report("or rule good -> Kfir is happy", True)

    def __str__(self):
        return f'{self.rule1} or {self.rule2}'

    def add_to_db(self):
        super().add_to_db()
        OrRule.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        OrRule.delete_record(self.rule_id, self.store_name)

    @staticmethod
    def create_instance_from_db_query(r):
        rule_id, store_name, rule_id1, rule_id2 = r.rule_id, r.store_name, r.rule_id1, r.rule_id2
        rule = OrRule()
        rule.rule_id1 = rule_id1
        rule.rule_id2 = rule_id2
        rule.set_db_info(store_name, rule_id)
        return rule

    @staticmethod
    def load_all_or_rules(store_name):
        out = {}
        records = DAL.load_all_by(OrRule, lambda r: r.store_name == store_name, OrRule.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.rule_id] = record
        return out

    @staticmethod
    def load_rule_by_id(store_name, rule_id):
        return DAL.load_all_by(OrRule, lambda r: r.store_name == store_name and r.rule_id == rule_id,
                                 OrRule.create_instance_from_db_query)


    @staticmethod
    def clear_db():
        DAL.clear(OrRule)

    @staticmethod
    def add_record(rule):
        DAL.add(rule)

    @staticmethod
    def delete_record(rule_id, store_name):
        DAL.delete(OrRule, lambda r: ((r.rule_id == rule_id) and (r.store_name == store_name)))