from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class StoreDiscount(IDiscountFor):
    def get_products_to_apply_discount_to(self, products: set[Product]):
        return products

    def __str__(self):
        return f'discount_for: store'