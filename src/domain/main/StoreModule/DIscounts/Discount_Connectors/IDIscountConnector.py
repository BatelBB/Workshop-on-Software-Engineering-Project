from abc import ABC, abstractmethod

from DataLayer.DAL import DAL
from domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.Utils.Logger import report
from src.domain.main.Utils.Response import Response


class IDiscountConnector(IDiscount):
    def __init__(self, id: int):
        super().__init__(id)
        self.children: list[IDiscount] = []
        self.children_ids = ""

    def add_discount_to_connector(self, discount, not_update=None) -> Response:
        if discount is None:
            return 1
        self.children.append(discount)
        self.children_ids += f'{discount.discount_id},'
        if not_update is None:
            DAL.update(self)
        return report("added discount", True)

    def find_discount(self, id: int):
        if self.check_id(id):
            return self
        for dis in self.children:
            d = dis.find_discount(id)
            if d is not None:
                return d
        return None

    def remove_discount(self, id) -> bool:
        for dis in self.children:
            if dis.discount_id == id:
                self.children.remove(dis)
                self.remove_child_from_child_ids(id)
                return True
            if dis.remove_discount(id):
                return True
        return False

    def replace(self, id, discount: IDiscount) -> bool:
        for dis in self.children:
            if dis.discount_id == id:
                self.children.remove(dis)
                self.remove_child_from_child_ids(id)
                self.add_discount_to_connector(discount)
                return True
            if dis.replace(id, discount):
                return True
        return False

    def remove_child_from_child_ids(self, child_id):
        numbers_list = self.children_ids.split(",")
        numbers_list = [num.strip() for num in numbers_list]
        if str(child_id) in numbers_list:
            numbers_list.remove(str(child_id))
        self.children_ids = ",".join(numbers_list)
        DAL.update(self)

    def get_parents_id(self, id) -> int:
        for dis in self.children:
            if dis.discount_id == id:
                return self.discount_id
            ret = dis.get_parents_id(id)
            if ret != -1:
                return ret
        return -1

    def __str__(self, indent):
        s = ""
        next_indent = f"{indent}\t"
        for d in self.children:
            s += f"{indent}child: {d.__str__(next_indent)} \n"
        return s

    def __repr__(self):
        s = ""
        for dis in self.children:
            s += f"id: {dis.discount_id}     "
        return s

    def get_all_simple_discounts(self, d) -> dict:
        for dis in self.children:
            d = dis.get_all_simple_discounts(d)
        return d

    def get_all_connectors(self, d) -> dict:
        for dis in self.children:
            d = dis.get_all_connectors(d)
        d[self.discount_id] = self.__repr__()
        return d

    def set_disconted_price_in_product(self, p: Product):
        return 0

    def set_db_info(self, discount_id, store_name, rule=None):
        self.store_name = store_name
        self.discount_id = discount_id

    def delete_from_db(self):
        for discount in self.children:
            discount.delete_from_db()
