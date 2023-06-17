from sqlalchemy import Column, Integer, String

from DataLayer.DAL import Base, DAL
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from src.domain.main.StoreModule.Product import Product
from src.domain.main.UserModule.Basket import Basket


class AddDiscounts(IDiscountConnector, Base):
    __tablename__ = 'add_discounts'
    __table_args__ = {'extend_existing': True}
    discount_id = Column("discount_id", Integer, primary_key=True)
    store_name = Column("store_name", String, primary_key=True)
    children_ids = Column("children_ids", String)

    def __init__(self, id: int):
        super().__init__(id)

    def apply_discount(self, basket: Basket, products: set[Product]):
        for discount in self.children:
            basket = discount.apply_discount(basket, products)
        return basket

    def is_level_o_discount(self, id: int) -> bool:
        for discount in self.children:
            if discount.check_id(id):
                return True
        return False

    def __str__(self, indent):
        return f"{indent}Add connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Add connector: {super().__repr__()}"

    def set_disconted_price_in_product(self, p: Product):
        for discount in self.children:
            p.discount_price -= discount.set_disconted_price_in_product(p)

    def add_to_db(self):
        AddDiscounts.add_record(self)

    def delete_from_db(self):
        super().delete_from_db()
        AddDiscounts.delete_record(self.discount_id, self.store_name)

    @staticmethod
    #returning an instance without the rule
    def create_instance_from_db_query(r):
        discount_id, store_name, children_ids\
            = r.discount_id, r.store_name, r.children_ids
        discount = AddDiscounts(discount_id)
        discount.children_ids = children_ids
        return discount

    @staticmethod
    def load_all_add_discounts(store_name):
        out = {}
        records = DAL.load_all_by(AddDiscounts, lambda r: r.store_name == store_name, AddDiscounts.create_instance_from_db_query)
        if not isinstance(records, list):
            records = [records]
        for record in records:
            out[record.discount_id] = record
        return out

    @staticmethod
    def load_add_discount_by_id(store_name, discount_id):
        return DAL.load_all_by(AddDiscounts, lambda r: r.store_name == store_name and r.discount_id == discount_id,
                               AddDiscounts.create_instance_from_db_query)

    @staticmethod
    def clear_db():
        DAL.clear(AddDiscounts)

    @staticmethod
    def add_record(discount):
        DAL.add(discount)

    @staticmethod
    def delete_record(discount_id, store_name):
        DAL.delete(AddDiscounts, lambda r: ((r.discount_id == discount_id) and (r.store_name == store_name)))