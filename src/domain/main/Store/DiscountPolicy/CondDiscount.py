from domain.main.Store.DiscountPolicy.IDiscountPolicy import IDiscountPolicy
from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.User.Basket import Basket


class CondDiscount(IDiscountPolicy):

    def __init__(self, simple_discount: IDiscountPolicy, rule: IRule):
        super().__init__(simple_discount.days_left)
        self.discount = simple_discount
        self.rule = rule

    def add_discount(self, discount: 'IDiscountPolicy'):
        self.discount.add_discount(discount)

    def calculate_price(self, basket: Basket, products: set[Product]):
        res = self.rule.enforce_rule(basket)
        if res.success and res.result:
            self.discount.calculate_price(basket, products)

    def get_discount_for_product(self, p_name, p_cur_price, products: set[Product]) -> str:
        dis = self.discount.get_discount_for_product(p_name, p_cur_price, products)
        if dis is not None:
            return f'{self.rule.__str__()} then discount: {dis}'
        return None

    def __str__(self):
        return f'discount_type: cond: \n rule: {self.rule.__str__()}\n discount: {self.discount.__str__()}'