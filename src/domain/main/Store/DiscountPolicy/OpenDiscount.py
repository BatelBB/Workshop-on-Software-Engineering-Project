from src.domain.main.Store.DiscountPolicy.DIscountsFor.IDiscountFor import IDiscountFor
from src.domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from src.domain.main.Store.Product import Product
from src.domain.main.UserModule.Basket import Basket, Item


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

    def get_discount_for_product(self, product_name, p_cur_price, products: set[Product]) -> str:
        discounted_products: set[Product] = self.discount_for.get_products_to_apply_discount_to(products)
        p_names = [p.name for p in discounted_products]
        if product_name in p_names:
            discounted_price = self.get_discount_price(p_cur_price)
            if self.next is not None:
                next_discount = self.next.get_discount_for_product(product_name, discounted_price, products)
                if next_discount is not None:
                    return f'original price = {p_cur_price} discounted price: {discounted_price}\n {next_discount}'
            return f'original price = {p_cur_price} discounted price: {discounted_price}'
        if self.next is not None:
            return self.next.get_discount_for_product(product_name, p_cur_price, products)
        return None

    def __str__(self):
        return f'discount_type: open, discount_percent: {self.percent}, {self.discount_for.__str__()}'

