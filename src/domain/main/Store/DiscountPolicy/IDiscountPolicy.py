from abc import ABC, abstractmethod

from src.domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from src.domain.main.Store.Product import Product
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class IDiscountPolicy(ABC):
    def __init__(self, days_left: int):
        self.next = None
        self.days_left = days_left

    def add_discount(self, discount: 'IDiscountPolicy'):
        if self.next is None:
            self.next = discount
        else:
            self.next.add_discount(discount)

    def calculate_next_discount(self, basket: Basket, products: set[Product]):
        if self.next is not None:
            self.next.calculate_price(basket, products)

    def new_day(self):
        self.days_left -= 1

    def delete_discount(self, index: int) -> Response:
        if index == 0:
            return None
        elif index == 1:
            #deleteing next:
            if self.next is None:
                return report_error("delete_discount", "no such discount")
            else:
                to_remove = self.next
                self.next = self.next.next
                return report(f"deleted: {to_remove.__str__()}", True)
        else:
            return self.next.delete_discount(index-1)




    @abstractmethod
    def get_discount_for_product(self, p_name, p_cur_price, products: set[Product]) -> str:
        ...

    @abstractmethod
    def calculate_price(self, basket: Basket, products: set[Product]):
        ...


