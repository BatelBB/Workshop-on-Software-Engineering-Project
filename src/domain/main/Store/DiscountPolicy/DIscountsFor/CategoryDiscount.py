from src.domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from src.domain.main.Store.Product import Product
from src.domain.main.UserModule.Basket import Basket


class CategoryDiscount(IDiscountFor):
    def __init__(self, cat_name):
        self.cat_name = cat_name

    def get_products_to_apply_discount_to(self, products: set[Product]):
        p = set()
        for product in products:
            if product.category == self.cat_name:
                p.add(product)
        return p

    def __str__(self):
        return f'discount_for: category: {self.cat_name}'
