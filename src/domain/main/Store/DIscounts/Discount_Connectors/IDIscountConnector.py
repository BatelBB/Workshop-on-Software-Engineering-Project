from abc import ABC, abstractmethod

from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Utils.Logger import report
from domain.main.Utils.Response import Response


class IDiscountConnector(IDiscount, ABC):
    def __init__(self, id: int):
        super().__init__(id)
        self.children: list[IDiscount] = []

    def add_discount_to_connector(self, discount) -> Response:
        self.children.append(discount)
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
            if dis.id == id:
                self.children.remove(dis)
                return True
            if dis.remove_discount(id):
                return True
        return False

    def replace(self, id, discount: IDiscount) -> bool:
        for dis in self.children:
            if dis.id == id:
                self.children.remove(dis)
                self.add_discount_to_connector(discount)
                return True
            if dis.replace(id, discount):
                return True
        return False

    def get_parents_id(self, id) -> int:
        for dis in self.children:
            if dis.id == id:
                return self.id
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



