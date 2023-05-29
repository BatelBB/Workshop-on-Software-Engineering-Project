from abc import ABC, abstractmethod

from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket


class IDiscountPolicy(ABC):
    def __init__(self, days_left: int):
        self.next = None
        self.days_left = days_left

    def add_discount(self, discount: 'IDiscountPolicy'):
        self.next = discount

    def calculate_next_discount(self, basket: Basket, products: set[Product]):
        if self.next is not None:
            self.next.calculate_price(basket, products)

    def new_day(self):
        self.days_left -= 1



    @abstractmethod
    def get_discount_for_product(self, p_name, p_cur_price, products: set[Product]) -> str:
        ...

    @abstractmethod
    def calculate_price(self, basket: Basket, products: set[Product]):
        ...
