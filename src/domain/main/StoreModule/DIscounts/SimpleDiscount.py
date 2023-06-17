from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket, Item


class SimpleDiscount(IDiscount, Base):
    __tablename__ = 'simple_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
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
        self.store_name = None
        if rule is not None:
            self.is_rule = 'False'
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
        d[self.id] = self.__repr__()
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
            return self.rule.set_db_info_as_discount_rule(store_name, discount_id - 1)
        return -1

    def add_to_db(self):
        SimpleDiscount.add_record(self)

    def delete_from_db(self):
        if self.rule is not None:
            self.rule.delete_from_db()
        SimpleDiscount.delete_record(self.rule_id, self.store_name)
