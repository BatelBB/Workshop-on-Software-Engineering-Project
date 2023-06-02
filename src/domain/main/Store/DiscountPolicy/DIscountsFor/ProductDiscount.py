from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket


class ProductDiscount(IDiscountFor):

    def __init__(self, product):
        self.product = product

    def get_products_to_apply_discount_to(self, products: set[Product]):
        if self.product in products:
            return {self.product}
        else:
            return {}

    def __str__(self):
        return f'discount_for: product: {self.product}'