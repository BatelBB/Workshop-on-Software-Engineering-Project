from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error


class XorDiscounts(IDiscountConnector, Base):
    __tablename__ = 'xor_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    children_ids = Column("children_ids", String)
    rule_id = Column("rule_id", Integer)

    def __init__(self, id: int, discount1: IDiscount=None, discount2: IDiscount=None, rule: IRule=None):
        super().__init__(id)
        if discount1 is not None:
            self.children.append(discount1)
            self.children.append(discount2)
        self.rule = rule
        self.rule_id = None

    def apply_discount(self, basket: Basket, products: set[Product]):
        if self.rule.enforce_rule(basket).success:
            return self.children[0].apply_discount(basket, products)
        return self.children[1].apply_discount(basket, products)

    def add_discount_to_connector(self, discount):
        return report_error("add_discount_to_connector", "cannot add discount to xor")

    def __str__(self, indent):
        return f"{indent}Xor connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Xor connector: {super().__repr__()}"

    def set_db_info(self, discount_id, store_name, rule=None):
        ans = super().set_db_info(discount_id, store_name, self.rule)
        self.children_ids = f"{self.children[0].discount_id},{self.children[1].discount_id},"
        self.rule_id = self.rule.rule_id
        return ans

    def add_to_db(self):
        self.rule.add_to_db()
        XorDiscounts.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        self.rule.delete_from_db()
        XorDiscounts.delete_record(self.discount_id, self.store_name)

    @staticmethod
    #returning an instance without the rule
    def create_instance_from_db_query(r):
        discount_id, store_name, children_ids, rule_id\
            = r.discount_id, r.store_name, r.children_ids, r.rule_id
        discount = XorDiscounts(discount_id)
        discount.children_ids = children_ids
        discount.rule_id = rule_id
        return discount

    @staticmethod
    def load_all_xor_discounts(store_name):
        out = {}
        records = DAL.load_all_by(XorDiscounts, lambda r: r.store_name == store_name, XorDiscounts.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.discount_id] = record
        return out

    @staticmethod
    def clear_db():
        DAL.clear(XorDiscounts)

    @staticmethod
    def add_record(discount):
        DAL.add(discount)

    @staticmethod
    def delete_record(discount_id, store_name):
        DAL.delete(XorDiscounts, lambda r: ((r.discount_id == discount_id) and (r.store_name == store_name)))