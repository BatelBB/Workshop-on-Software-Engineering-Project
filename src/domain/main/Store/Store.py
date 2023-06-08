import threading

from multipledispatch import dispatch

from domain.main.Store.DIscounts.Discount_Connectors.AddDiscounts import AddDiscounts
from domain.main.Store.DIscounts.Discount_Connectors.MaxDiscounts import MaxDiscounts
from domain.main.Store.DIscounts.Discount_Connectors.OrDiscounts import OrDiscounts
from domain.main.Store.DIscounts.Discount_Connectors.XorDiscounts import XorDiscounts
from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.SimpleDiscount import SimpleDiscount
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService, provisionService
from src.domain.main.Store.Product import Product
from src.domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.Store.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from src.domain.main.Store.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Logger import report_error, report
from src.domain.main.Utils.Response import Response


class ProductQuantity:
    def __init__(self, quantity: int):
        self.quantity = quantity
        self.lock = threading.RLock()

    def reserve(self, desired_quantity: int) -> bool:
        with self.lock:
            if self.quantity > desired_quantity:
                self.quantity -= desired_quantity
                return True
            else:
                return False

    def refill(self, additional_quantity: int) -> int:
        with self.lock:
            new_quantity = max(self.quantity + additional_quantity, 0)
            self.quantity = new_quantity
            return new_quantity

    def reset(self, new_quantity: int) -> None:
        with self.lock:
            self.quantity = new_quantity


class Store:
    def __init__(self, name: str):
        self.name = name
        self.products: set[Product] = set()
        self.products_quantities: dict[str, ProductQuantity] = dict()
        self.purchase_history: list[str] = list()
        self.provisionService: IProvisionService = provisionService()
        self.products_with_special_purchase_policy: dict[str:IPurchasePolicy] = {}
        self.products_with_bid_purchase_policy: dict[str: BidPolicy] = {}
        self.purchase_rules: dict[int:IRule] = {}
        self.purchase_rule_ids = 0
        self.purchase_rule_lock = threading.RLock()
        self.discounts: AddDiscounts = AddDiscounts(0)
        self.discount_counter = 0
        self.discount_lock = threading.RLock()

    def __str__(self):
        output: str = f'Store: {self.name}\nProducts:\n'
        for i, product in enumerate(self.products):
            output += f'{i}).\t{product.name}. Available quantity: {self.products_quantities[product.name].quantity}.\n'
        return output

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __dic__(self):
        out = {}
        for p in self.products:
            p_d = p.__dic__()
            p_d["Quantity"] = self.products_quantities.get(p.name).quantity
            out[p.name] = p_d
        return out

    def get_name(self):
        return self.name

    def find(self, product_name: str) -> Product | None:
        filtered = list(filter(lambda p: p.name == product_name, self.products))
        return filtered.pop() if len(filtered) > 0 else None

    def contains(self, product_name: str) -> bool:
        return self.find(product_name) is not None

    def add(self, product: Product, quantity: int) -> None:
        if product not in self.products:
            self.products.add(product)
            self.products_quantities.update({product.name: ProductQuantity(quantity)})
        else:
            self.products_quantities[product.name].refill(quantity)

    def update(self, product_name: str, quantity: int) -> bool:
        p = Product(product_name)
        is_succeed = p in self.products
        if is_succeed:
            self.products_quantities[product_name].reset(quantity)
        return is_succeed

    def remove(self, product_name: str) -> bool:
        p = Product(product_name)
        try:
            self.products.remove(p)
            del self.products_quantities[product_name]
            return True
        except KeyError:
            return False

    def get_product(self, product_name: str) -> Response[Product] | Response[bool]:
        return Response(product_name) if self.contains(product_name) else report_error(self.get_product.__qualname__,
                                                                                       f'Store \'{self.name}\' does not contains Product \'{product_name}\'')

    def get_all(self) -> set[Product]:
        return self.products

    def amount_of(self, product_name: str) -> int:
        return self.products_quantities[product_name].quantity if product_name in self.products_quantities else 0

    def get_product_price(self, product_name: str) -> float:
        p = self.find(product_name)
        return p.price if p is not None else 0.000

    def get_product_discounts_str(self, p_name: str) -> str:
        return "0"

    def refill(self, reserved: dict[str, int]) -> None:
        for product_name, reserved_quantity in reserved.items():
            self.products_quantities[product_name].refill(reserved_quantity)

    @dispatch(str, int)
    def reserve(self, product_name: str, quantity: int) -> bool:
        return self.products_quantities[product_name].reserve(quantity)

    @dispatch(Basket)
    def reserve(self, basket: Basket) -> bool:
        reserved: dict[str, int] = dict()
        is_reservation_succeed = True
        for item in basket.items:
            is_reservation_succeed = is_reservation_succeed and self.reserve(item.product_name, item.quantity)
            if is_reservation_succeed:
                reserved[item.product_name] = item.quantity
            else:
                break
        if not is_reservation_succeed:
            self.refill(reserved)
        return is_reservation_succeed

    def get_products_by(self, predicate) -> dict[str, dict]:
        acc = {}
        for p in list(filter(predicate, self.products)):
            acc.update({p.name: p.__dic__()})
        return acc

    def change_product_name(self, old: str, new: str) -> bool:
        product = self.find(old)
        is_changed = product is not None
        if is_changed:
            self.products.remove(product)
            q = self.products_quantities[old]
            del self.products_quantities[old]
            self.products_quantities.update({new: q})
            product.name = new
            self.products.add(product)
        return is_changed

    def change_product_category(self, old: str, new: str) -> bool:
        product = self.find(old)
        is_changed = product is not None
        if is_changed:
            self.products.remove(product)
            product.category = new
            self.products.add(product)
        return is_changed

    def change_product_price(self, old: float, new: float) -> None:
        for product in filter(lambda p: p.price == old, self.products):
            product.price = new

    def enforce_purchase_rules(self, basket: Basket) -> Response[bool]:
        for rule in self.purchase_rules:
            res = self.purchase_rules[rule].result.enforce_rule(basket)
            if not res.success:
                return res
        return report("all rules are kept: Kfir is happy!", True)

    def reserve_products(self, basket: Basket) -> bool:
        res = self.enforce_purchase_rules(basket)
        if not res.success:
            return False

        reserved: dict[str, int] = dict()
        is_reservation_succeed = True
        for item in basket.items:
            is_reservation_succeed = is_reservation_succeed and self.reserve(item.product_name, item.quantity)
            if is_reservation_succeed:
                reserved[item.product_name] = item.quantity
            else:
                break
        if not is_reservation_succeed:
            self.refill(reserved)
        return is_reservation_succeed

    def get_products(self, predicate) -> list[Product]:
        return list(filter(predicate, self.products))

    def get_products_dict(self, predicate) -> dict:
        l = list(filter(predicate, self.products))
        dict = {}
        for p in l:
            dict[p.name] = p.__dic__()
        return dict

    def get_products_by_name(self, name: str) -> dict[Product]:
        return self.get_products_dict(lambda p: name in p.keywords)

    def get_products_by_category(self, category: str) -> dict[Product]:
        return self.get_products_dict(lambda p: category == p.category)

    def get_products_by_price(self, price: float) -> dict[Product]:
        return self.get_products_dict(lambda p: price == p.price)

    def get_products_by_keywords(self, keywords: list[str]) -> list[Product]:
        return self.get_products(lambda p: len((set(p.keywords) & set(keywords))) > 0)

    def update_basket_to_current_price(self, basket: Basket):
        for i in basket.items:
            i.price = self.get_product_price(i.product_name)
            i.discount_price = i.price

    def calculate_basket_price(self, basket: Basket) -> float:
        self.update_basket_to_current_price(basket)
        basket = self.discounts.apply_discount(basket, self.products)
        price = 0
        # only call from right after reserve
        for item in basket.items:
            price += item.discount_price * item.quantity
        return price

    def add_to_purchase_history(self, baskets: Basket):
        self.purchase_history.append(baskets.__str__())

    def get_purchase_history(self) -> str:
        output = "Purchase history:\n"
        for item in self.purchase_history:
            output += f'{item}\n'
        return output

    def add_product_to_special_purchase_policy(self, product_name: str, p_policy: IPurchasePolicy) -> Response[bool]:
        if not self.reserve(product_name, 1):
            return report_error("add_product_to_special_purchase_policy",
                                f'cannot reserve product {product_name} for special purchase policy')

        if product_name in self.products_with_special_purchase_policy.keys():
            return report_error("add_product_to_special_purchase_policy",
                                "product can have only 1 special purchase policy")

        self.products_with_special_purchase_policy[product_name] = p_policy
        return report("add_product_to_special_purchase_policy", True)

    def add_product_to_bid_purchase_policy(self, product_name: str, p_policy: IPurchasePolicy, staff: list[str]) -> \
    Response[bool]:
        if not self.reserve(product_name, 1):
            return report_error("add_product_to_bid_purchase_policy",
                                f'cannot reserve product {product_name} for special purchase policy')

        if product_name in self.products_with_bid_purchase_policy.keys():
            return report_error("add_product_to_bid_purchase_policy", "product can have only 1 special purchase policy")

        self.products_with_bid_purchase_policy[product_name] = p_policy
        self.set_to_approve_for_bid(product_name, staff)
        return report("add_product_to_bid_purchase_policy", True)

    def apply_purchase_policy(self, payment_service: IPaymentService, product_name: str,
                              delivery_service: IProvisionService, how_much: float) -> Response[bool]:
        if product_name not in self.products_with_special_purchase_policy.keys() and product_name not in self.products_with_bid_purchase_policy.keys():
            return report_error("apply_purchase_policy", "product only has immediate purchase policy")

        policy: IPurchasePolicy
        if product_name in self.products_with_special_purchase_policy.keys():
            policy = self.products_with_special_purchase_policy[product_name]
        elif product_name in self.products_with_bid_purchase_policy.keys():
            policy = self.products_with_bid_purchase_policy[product_name]

        return policy.apply_policy(payment_service, delivery_service, how_much)

    def new_day(self):
        list_to_remove = []
        for p in self.products_with_special_purchase_policy.keys():
            self.products_with_special_purchase_policy[p].new_day()
            if self.products_with_special_purchase_policy[p].is_active == 0:
                list_to_remove.append(p)

        for p in list_to_remove:
            self.products_with_special_purchase_policy.pop(p)

    def set_to_approve_for_bid(self, product_name: str, staff: list[str]):
        self.products_with_bid_purchase_policy[product_name].set_approval_dict_in_bid_policy(staff)

    def approve_bid(self, person: str, product_name: str, is_approve: bool):
        if product_name not in self.products_with_bid_purchase_policy.keys():
            return report_error("approve_bid", f"{product_name} not in bidding policy")

        return self.products_with_bid_purchase_policy[product_name].approve(person)

    def add_purchase_rule(self, rule: IRule) -> Response:
        with self.purchase_rule_lock:
            self.purchase_rules[self.purchase_rule_ids] = rule
            self.purchase_rule_ids += 1
            return report("add_purchase_rule -> success", True)

    def get_purchase_rules(self):
        return self.purchase_rules

    def remove_purchase_rule(self, rule_id: int):
        self.purchase_rules.pop(rule_id)

    def add_simple_discount(self, percent: int, discount_type: str, rule: IRule = None, discount_for_name=None) -> Response[bool]:
        with self.discount_lock:
            self.discount_counter += 1
            discount = SimpleDiscount(self.discount_counter, percent, discount_type, rule, discount_for_name)
            self.discounts.add_discount_to_connector(discount)

    def connect_discounts(self, id1, id2, connection_type, rule=None) -> Response:
        with self.discount_lock:
            # find
            d1 = self.discounts.find_discount(id1)
            d2 = self.discounts.find_discount(id2)
            if d1 is None or d2 is None:
                return report_error("connecet_discounts", "discount not found")

            # create new connector
            self.discount_counter += 1
            new_id = self.discount_counter
            if connection_type == "add":
                conn = AddDiscounts(new_id)
            elif connection_type == "or":
                conn = OrDiscounts(new_id)
            elif connection_type == "max":
                conn = MaxDiscounts(new_id)
            elif connection_type == "xor":
                conn = XorDiscounts(new_id, d1, d2, rule)
            else:
                return report_error("connect_discounts", f"invalide discount connection type: {connection_type}")

            # delete d1 from tree
            id_for_backtrack = self.discounts.get_parents_id(id1)
            self.discounts.remove_discount(id1)

            conn.add_discount_to_connector(d1)
            conn.add_discount_to_connector(d2)

            # replace 2nd discount with new connector in discount tree
            if self.discounts.replace(id2, conn):
                return report("successfully connected discounts", True)
            else:
                self.discounts.find_discount(id_for_backtrack).add_discount_to_connector(d1)
                return report_error("connect_discounts", "unsuccessful connection of discounts")

    def get_product_obj(self, p_name):
        p_names = [p.name for p in self.products]
        if p_name in p_names:
            return Response(self.find(p_name), "product found")
        else:
            return report_error("get_product_obj", "product doesnt exsist")

    def get_products_with_discounts(self) -> dict[Product:str]:
        return report_error("delete_discount", "no implemented")

    def get_discounts(self):
        return report_error("delete_discount", "no implemented")

    def delete_discount(self, id: int) -> Response:
        if self.discounts.remove_discount(id):
            return report(f"discount {id} has been removeed", True)
        return report_error("delete_discount", f"discount {id} has been removeed")

    def add_owner(self, name: str):
        for key in self.products_with_bid_purchase_policy.keys():
            policy = self.products_with_bid_purchase_policy[key]
            policy.add_to_approval_dict_in_bid_policy(name)
