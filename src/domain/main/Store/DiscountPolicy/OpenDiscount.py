from domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket, Item


class OpenDiscount(IDiscountPolicy):

    def __init__(self, percent: int, discount_for: IDiscountFor, days_left: int):
        super().__init__(discount_for, days_left, percent)
        self.percent = percent

    def calculate_price(self, basket: Basket, products: set[Product]):
        discounted_products: set[Product] = super().get_dis_for(products)
        i_names = [i.product_name for i in basket.items]
        for p in discounted_products:
            if p.name in i_names:
                basket.get_item(p.name).price = super().get_discount_price(p.price)

        super().calculate_next_discount(basket, products)

    def get_discount_for_product(self, product, p_cur_price, products: set[Product]) -> str:
        discounted_products: set[Product] = super().discount_for.get_products_to_apply_discount_to(products)
        p_names = [p.name for p in discounted_products]
        if product.name in p_names:
            discounted_price = super().get_discount_price(p_cur_price)
            return f'original price = {p_cur_price}///only now for {discounted_price}'



