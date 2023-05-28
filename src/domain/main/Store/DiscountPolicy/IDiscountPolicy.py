from abc import ABC, abstractmethod

from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket


class IDiscountPolicy(ABC):
    def __init__(self, discount_for: IDiscountFor, days_left: int, percent: int):
        self.discount_for = discount_for
        self.next = None
        self.days_left = days_left
        self.percent = percent

    def get_dis_for(self, products):
        return self.discount_for.get_products_to_apply_discount_to(products)

    def add_discount(self, discount: 'IDiscountPolicy'):
        self.next = discount

    def calculate_next_discount(self, basket: Basket, products: set[Product]):
        if self.next is not None:
            self.next.calculate_price(basket, products)

    def new_day(self):
        self.days_left -= 1

    def get_discount_price(self, original_price):
        return original_price * (0.01 * (100-self.percent))

    @abstractmethod
    def get_discount_for_product(self, p_name, p_cur_price, products: set[Product]) -> str:
        ...

    @abstractmethod
    def calculate_price(self, basket: Basket, products: set[Product]):
        ...
