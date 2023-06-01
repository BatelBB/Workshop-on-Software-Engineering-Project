from domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.User.Basket import Basket, Item


class XorDiscount(IDiscountPolicy):
    def __init__(self, simple_discount1: IDiscountPolicy, simple_discount2: IDiscountPolicy, rule: IRule, days_left: int):
        super().__init__(days_left)
        self.discount1 = simple_discount1
        self.discount2 = simple_discount2
        self.rule = rule

    def get_discount_for_product(self, p_name, p_cur_price, products: set[Product]) -> str:
        return "0"

    def deep_copy_item(self, i: Item):
        cpy = Item(i.product_name, i.quantity, i.price)
        cpy.discount_price = i.discount_price
        return cpy

    def deep_copy_basket(self, basket: Basket) -> Basket:
        new_basket = Basket()
        for i in basket.items:
            new_basket.add_item(self.deep_copy_item(i))
        return new_basket

    def calc_cur_price(self, basket:Basket) -> float:
        price = 0
        for i in basket.items:
            price += (i.discount_price * i.quantity)
        return price

    def calculate_price(self, basket: Basket, products: set[Product]):
        res = self.rule.enforce_rule(basket)
        if not res.success:
            return res

        b1 = self.deep_copy_basket(basket)
        self.discount1.calculate_price(b1, products)

        b2 = self.deep_copy_basket(basket)
        self.discount2.calculate_price(b2, products)

        if self.calc_cur_price(b1) > self.calc_cur_price(b2):
            self.discount2.calculate_price(basket, products)
        else:
            self.discount1.calculate_price(basket, products)

