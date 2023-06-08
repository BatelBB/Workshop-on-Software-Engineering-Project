from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.UserModule.Basket import Basket, Item


class SimpleDiscount(IDiscount):
    # discount_type = store | category | product
    # discount_for_name: in case discount_type = product -> product_name |
    #                            discount_type = category -> category_name
    #
    def __init__(self, id: int,  percent: int, discount_type: str, rule: IRule = None, discount_for_name=None):
        super().__init__(id)
        self.percent = percent
        self.discount_type = discount_type
        self.rule = rule
        self.discount_for_name = discount_for_name

    def apply_for_product(self, item: Item, product: Product):
        if (self.discount_type == "category" and product.category == self.discount_for_name) \
                or (self.discount_type == "product" and product.name == self.discount_for_name) \
                or (self.discount_type == "store"):
            return item.price * (self.percent) * 0.01

        return item.discount_price

    def find(self, product_name: str, products: set[Product]) -> Product | None:
        filtered = list(filter(lambda p: p.name == product_name, products))
        return filtered.pop() if len(filtered) > 0 else None

    def apply_discount(self, basket: Basket, products: set[Product]) -> Basket:
        if self.rule is not None:
            res = self.rule.enforce_rule(basket)
            if not res.success:
                return basket

        items = basket.items
        for i in items:
            p = self.find(i.product_name, products)
            if p is None:
                basket.remove_item(i)
            else:
                i.discount_price -= self.apply_for_product(i, p)
        return basket

    def remove_discount(self, id) -> bool:
        return False

    def replace(self, id, discount) -> bool:
        return False

    def get_parents_id(self, id) -> int:
        return -1
