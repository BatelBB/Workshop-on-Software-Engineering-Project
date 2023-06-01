from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket, Item


class OpenDiscount(IDiscountPolicy):

    def __init__(self, percent: int, discount_for: IDiscountFor, days_left: int):
        super().__init__(days_left)
        self.percent = percent
        self.discount_for = discount_for


    def get_discount_price(self, original_price):
        return original_price * (0.01 * (100-self.percent))

    def get_dis_for(self, products):
        return self.discount_for.get_products_to_apply_discount_to(products)

    def calculate_price(self, basket: Basket, products: set[Product]):
        discounted_products: set[Product] = self.get_dis_for(products)
        i_names = [i.product_name for i in basket.items]
        for p in discounted_products:
            if p.name in i_names:
                basket.get_item(p.name).discount_price = self.get_discount_price(basket.get_item(p.name).discount_price)

        super().calculate_next_discount(basket, products)

    def get_discount_for_product(self, product, p_cur_price, products: set[Product]) -> str:
        discounted_products: set[Product] = self.discount_for.get_products_to_apply_discount_to(products)
        p_names = [p.name for p in discounted_products]
        if product.name in p_names:
            discounted_price = self.get_discount_price(p_cur_price)
            return f'original price = {p_cur_price}///only now for {discounted_price}'



