from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket, Item


class SimpleDiscount(IDiscount, Base):
    __tablename__ = 'simple_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    percent = Column("percent", Integer)
    discount_type = Column("discount_type", String)
    discount_for_name = Column("discount_for_name", String)
    is_rule = Column("is_rule", String)
    rule_id = Column("rule_id", Integer)

    # discount_type = store | category | product
    # discount_for_name: in case discount_type = product -> product_name |
    #                            discount_type = category -> category_name
    #
    def __init__(self, id: int, percent: int, discount_type: str, rule: IRule = None, discount_for_name=None):
        super().__init__(id)
        self.percent = percent
        self.discount_type = discount_type
        self.rule = rule
        self.discount_for_name = discount_for_name
        if rule is None:
            self.is_rule = 'False'
            self.rule_id = 0
        else:
            self.is_rule = 'True'

    def apply_for_product(self, item: Item, product: Product):
        if (self.discount_type == "category" and product.category == self.discount_for_name) \
                or (self.discount_type == "product" and product.name == self.discount_for_name) \
                or (self.discount_type == "store"):
            return item.price * (self.percent) * 0.01

        return item.discount_price

    def find(self, product_name: str, products: set[Product]) -> Product | None:
        filtered = list(filter(lambda p: p.name == product_name, products))
        return filtered.pop() if len(filtered) > 0 else None

    def apply_discount(self, basket: Basket, products: set[Product]) -> Basket:
        if self.rule is not None:
            res = self.rule.enforce_rule(basket)
            if not res.success:
                return basket

        items = basket.items
        for i in items:
            p = self.find(i.product_name, products)
            if p is None:
                basket.remove_item(i)
            else:
                i.discount_price -= self.apply_for_product(i, p)
        return basket

    def remove_discount(self, id) -> bool:
        return False

    def replace(self, id, discount) -> bool:
        return False

    def get_parents_id(self, id) -> int:
        return -1

    def __str__(self, indent):
        s = ""
        if self.discount_type == "store":
            s = "store"
        else:
            s = self.discount_for_name
        return f"{indent}simple discount: {self.percent}% for {s}"

    def __repr__(self):
        s = ""
        if self.discount_type == "store":
            s = "store"
        else:
            s = self.discount_for_name
        return f"simple discount: {self.percent}% for {s}"

    def get_all_simple_discounts(self, d) -> dict:
        d[self.discount_id] = self.__repr__()
        return d

    def get_all_connectors(self, d):
        return d

    def set_disconted_price_in_product(self, p: Product):
        if self.discount_type == "store" or self.discount_for_name == p.name or self.discount_for_name == p.category:
            return self.percent * p.price * 0.01
        return 0

    def set_db_info(self, discount_id, store_name, rule=None):
        self.store_name = store_name
        self.discount_id = discount_id
        if rule is not None:
            self.rule_id = discount_id + 1
            return 1 + self.rule.set_db_info(f"{store_name}_discount", discount_id + 1)
        return 1

    def add_to_db(self):
        if self.rule is not None:
            self.rule.add_to_db()
        SimpleDiscount.add_record(self)

    def delete_from_db(self):
        if self.rule is not None:
            self.rule.delete_from_db()
        SimpleDiscount.delete_record(self.discount_id, self.store_name)

    def load_my_rule_from_db(self):
        if self.is_rule:
            rule = SimpleRule.load_rule_by_id(f'{self.store_name}_discount', self.rule_id)



    @staticmethod
    #returning an instance without the rule
    def create_instance_from_db_query(r):
        discount_id, store_name, percent, discount_type, discount_for_name, is_rule, rule_id\
            = r.discount_id, r.store_name, r.percent, r.discount_type, r.discount_for_name, r.is_rule, r.rule_id
        discount = SimpleDiscount(discount_id, percent, discount_type, discount_for_name=discount_for_name)
        if is_rule == 'True':
            discount.is_rule = is_rule
            discount.rule_id = rule_id
        return discount

    @staticmethod
    def load_all_simple_discounts(store_name):
        out = {}
        records = DAL.load_all_by(SimpleDiscount, lambda r: r.store_name == store_name, SimpleDiscount.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.discount_id] = record
        return out

    @staticmethod
    def clear_db():
        DAL.clear(SimpleDiscount)

    @staticmethod
    def add_record(discount):
        DAL.add(discount)

    @staticmethod
    def delete_record(discount_id, store_name):
        DAL.delete(SimpleDiscount, lambda r: ((r.discount_id == discount_id) and (r.store_name == store_name)))
