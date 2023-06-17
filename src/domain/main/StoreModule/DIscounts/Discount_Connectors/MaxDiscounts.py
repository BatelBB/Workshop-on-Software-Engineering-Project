from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from src.domain.main.StoreModule.Product import Product
from src.domain.main.UserModule.Basket import Basket


class MaxDiscounts(IDiscountConnector, Base):
    __tablename__ = 'max_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    children_ids = Column("children_ids", String)

    def __init__(self, id: int):
        super().__init__(id)

    def apply_discount(self, basket: Basket, products: set[Product]):
        basket_save = basket.deep_copy()
        best_price = basket.calc_price()

        for discount in self.children:
            next_basket = discount.apply_discount(basket.deep_copy(), products)
            if next_basket.calc_price() < best_price:
                best_price = next_basket.calc_price()
                basket_save = next_basket.deep_copy()

        return basket_save

    def __str__(self, indent):
        return f"{indent}Max connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Max connector: {super().__repr__()}"

    def add_to_db(self):
        MaxDiscounts.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        MaxDiscounts.delete_record(self.discount_id, self.store_name)

    @staticmethod
    # returning an instance without the rule
    def create_instance_from_db_query(r):
        discount_id, store_name, children_ids \
            = r.discount_id, r.store_name, r.children_ids
        discount = MaxDiscounts(discount_id)
        discount.children_ids = children_ids
        return discount

    @staticmethod
    def load_all_max_discounts(store_name):
        out = {}
        records = DAL.load_all_by(MaxDiscounts, lambda r: r.store_name == store_name,
                                  MaxDiscounts.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.discount_id] = record
        return out

    @staticmethod
    def clear_db():
        DAL.clear(MaxDiscounts)

    @staticmethod
    def add_record(discount):
        DAL.add(discount)

    @staticmethod
    def delete_record(discount_id, store_name):
        DAL.delete(MaxDiscounts, lambda r: ((r.discount_id == discount_id) and (r.store_name == store_name)))
