from sqlalchemy import Column, Integer, String

from domain.main.Utils import Base_db
from src.domain.main.StoreModule.PurchaseRules.RuleCombiner.IRuleCombiner import IRuleCombiner
from src.domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report
from src.domain.main.Utils.Response import Response


class AndRule(IRuleCombiner, Base_db.Base):
    __tablename__ = 'and_rules'
    __table_args__ = {'extend_existing': True}
    id = Column("id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    id1 = Column("id1", Integer)
    id2 = Column("id2", Integer)
    def __init__(self, r1: SimpleRule, r2: SimpleRule):
        super().__init__(r1, r2)

    def enforce_rule(self, basket: Basket) -> Response[bool]:
        con1 = self.rule1.enforce_rule(basket)
        con2 = self.rule2.enforce_rule(basket)

        if not con1.success:
            return con1
        elif not con2.success:
            return con2
        return report("and rule good -> Kfir is happy" ,True)

    def __str__(self):
        return f'{self.rule1} and {self.rule2}'