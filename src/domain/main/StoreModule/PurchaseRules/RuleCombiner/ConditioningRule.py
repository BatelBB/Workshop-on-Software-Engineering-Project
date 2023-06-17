from sqlalchemy import Integer, Column, String

from DataLayer.DAL import Base, DAL
from domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.IRuleCombiner import IRuleCombiner
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report
from src.domain.main.Utils.Response import Response


class ConditioningRule(IRuleCombiner, Base):
    __tablename__ = 'cond_rules'
    __table_args__ = {'extend_existing': True}
    rule_id = Column("rule_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    rule_id1 = Column("rule_id1", Integer)
    rule_id2 = Column("rule_id2", Integer)

    def __init__(self, r1: IRule = None, r2: IRule = None):
        super().__init__(r1, r2)

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        con1 = self.rule1.enforce_rule(basket)
        con2 = self.rule2.enforce_rule(basket)

        if con1.success and not con2.success:
            return con2
        return report("conditioning rule good -> Kfir is happy", True)

    def __str__(self):
        return f'if {self.rule1} then must be also {self.rule2}'

    def add_to_db(self):
        super().add_to_db()
        ConditioningRule.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        ConditioningRule.delete_record(self.rule_id, self.store_name)

    @staticmethod
    def create_instance_from_db_query(r):
        rule_id, store_name, rule_id1, rule_id2 = r.rule_id, r.store_name, r.rule_id1, r.rule_id2
        rule = ConditioningRule()
        rule.rule_id1 = rule_id1
        rule.rule_id2 = rule_id2
        rule.set_db_info(store_name, rule_id)
        return rule

    @staticmethod
    def load_all_cond_rules(store_name):
        out = {}
        records = DAL.load_all_by(ConditioningRule, lambda r: r.store_name == store_name, ConditioningRule.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.rule_id] = record
        return out

    @staticmethod
    def clear_db():
        DAL.clear(ConditioningRule)

    @staticmethod
    def add_record(rule):
        DAL.add(rule)

    @staticmethod
    def delete_record(rule_id, store_name):
        DAL.delete(ConditioningRule, lambda r: ((r.rule_id == rule_id) and (r.store_name == store_name)))
