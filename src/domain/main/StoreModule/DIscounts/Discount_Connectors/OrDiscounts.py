from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from src.domain.main.StoreModule.Product import Product
from src.domain.main.UserModule.Basket import Basket


class OrDiscounts(IDiscountConnector, Base):
    __tablename__ = 'or_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    children_ids = Column("children_ids", String)

    def __init__(self, id: int):
        super().__init__(id)

    # returns the min discount
    def apply_discount(self, basket: Basket, products: set[Product]):
        initial = basket.calc_price()

        basket1 = basket.deep_copy()
        basket2 = basket.deep_copy()

        basket1 = self.children[0].apply_discount(basket1, products)
        price1 = basket1.calc_price()
        basket2 = self.children[1].apply_discount(basket2, products)
        price2 = basket2.calc_price()

        if price1 == initial:
            return basket2
        elif price2 == initial:
            return basket1
        elif price1 > price2:
            return basket1
        else:
            return basket2


    def __str__(self, indent):
        return f"{indent}Or connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Or connector: {super().__repr__()}"


    def add_to_db(self):
        OrDiscounts.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        OrDiscounts.delete_record(self.discount_id, self.store_name)

    @staticmethod
    # returning an instance without the rule
    def create_instance_from_db_query(r):
        discount_id, store_name, children_ids \
            = r.discount_id, r.store_name, r.children_ids
        discount = OrDiscounts(discount_id)
        discount.children_ids = children_ids
        return discount

    @staticmethod
    def load_all_add_discounts(store_name):
        out = {}
        records = DAL.load_all_by(OrDiscounts, lambda r: r.store_name == store_name,
                                  OrDiscounts.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.discount_id] = record
        return out

    @staticmethod
    def clear_db():
        DAL.clear(OrDiscounts)

    @staticmethod
    def add_record(discount):
        DAL.add(discount)

    @staticmethod
    def delete_record(discount_id, store_name):
        DAL.delete(OrDiscounts, lambda r: ((r.discount_id == discount_id) and (r.store_name == store_name)))