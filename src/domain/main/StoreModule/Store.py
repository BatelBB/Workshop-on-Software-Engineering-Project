import threading
from itertools import chain

from multipledispatch import dispatch
from sqlalchemy import Column, String

from DataLayer.DAL import DAL, Base
from domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.StoreModule.PurchaseRules.BasketRule import BasketRule
from domain.main.StoreModule.PurchaseRules.RuleCombiner.AndRule import AndRule
from domain.main.StoreModule.PurchaseRules.RuleCombiner.ConditioningRule import ConditioningRule
from domain.main.StoreModule.PurchaseRules.RuleCombiner.OrRule import OrRule
from domain.main.StoreModule.PurchaseRules.SimpleRule import SimpleRule
from domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.AddDiscounts import AddDiscounts
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.MaxDiscounts import MaxDiscounts
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.OrDiscounts import OrDiscounts
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.XorDiscounts import XorDiscounts
from src.domain.main.StoreModule.DIscounts.SimpleDiscount import SimpleDiscount
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService, provisionService
from src.domain.main.StoreModule.Product import Product
from src.domain.main.StoreModule.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.StoreModule.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from src.domain.main.StoreModule.PurchaseRules.IRule import IRule
from src.domain.main.UserModule.Basket import Basket, Item
from src.domain.main.Utils.Logger import report_error, report, report_info
from src.domain.main.Utils.Response import Response


class ProductQuantity:
    def __init__(self, quantity: int):
        self.quantity = quantity
        self.lock = threading.RLock()

    def reserve(self, desired_quantity: int) -> bool:
        with self.lock:
            if self.quantity >= desired_quantity:
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


class Store(Base):
    __tablename__ = 'stores'
    __table_args__ = {'extend_existing': True}
    name = Column("name", String, primary_key=True)
    purchase_history_str = Column("purchase_history_str", String, default='')

    def __init__(self, name: str):
        self.name = name
        self.products: set[Product] = set()
        self.products_quantities: dict[str, ProductQuantity] = dict()
        self.purchase_history: list[str] = list()
        self.products_with_special_purchase_policy: dict[str:IPurchasePolicy] = {}
        self.products_with_bid_purchase_policy: dict[str: BidPolicy] = {}
        self.purchase_rules: dict[int:IRule] = {}
        self.purchase_rule_ids = 0
        self.purchase_rule_lock = threading.RLock()
        self.discounts = None
        self.init_discounts()
        self.discount_counter = 1
        self.discount_lock = threading.RLock()
        self.discount_rule_counter = 0

    def init_discounts(self):
        root = AddDiscounts.load_add_discount_by_id(self.name, 0)
        if root:
            self.discounts = root[0]
            self.discounts.set_db_info(self.name, root[0].discount_id)
        else:
            self.discounts: AddDiscounts = AddDiscounts(0)
            self.discounts.set_db_info(0, self.name)
            self.discounts.add_to_db()

    @staticmethod
    def create_instance_from_db_query(r):
        store_name, purchase_history_str = r.name, r.purchase_history_str
        store = Store(store_name)

        for p in Product.load_products_of(store_name):
            store.add(p, p.quantity)

        for purchase in purchase_history_str.split('#'):
            store.purchase_history.append(purchase)

        try:
            store.purchase_history.remove('')  # drop default db value
        except ValueError:
            pass

        return store

    def load_or_rules_db(self):
        # assuming self.purchase_rules loaded all irules
        or_rules_dict = OrRule.load_all_or_rules(self.name)
        for rule_id, rule in or_rules_dict.items():
            self.set_child_rules(rule)
        return or_rules_dict

    def load_and_rules_db(self):
        # assuming self.purchase_rules loaded all irules
        and_rules_dict = AndRule.load_all_and_rules(self.name)
        for rule_id, rule in and_rules_dict.items():
            self.set_child_rules(rule)
        return and_rules_dict

    def load_cond_rules_db(self):
        # assuming self.purchase_rules loaded all irules
        cond_rules_dict = ConditioningRule.load_all_cond_rules(self.name)
        for rule_id, rule in cond_rules_dict.items():
            self.set_child_rules(rule)
        return cond_rules_dict

    def set_child_rules(self, complex_rule):
        rule1 = self.purchase_rules.pop(complex_rule.rule_id + 1)
        rule2 = self.purchase_rules.pop(complex_rule.rule_id + 2)
        complex_rule.rule1 = rule1
        complex_rule.rule2 = rule2

    def load_my_rules(self):
        simple_rule_dict = SimpleRule.load_all_simple_rules(self.name)
        basket_rules_dict = BasketRule.load_all_basket_rules(self.name)
        self.purchase_rules = simple_rule_dict
        self.purchase_rules.update(basket_rules_dict)

        or_rules = self.load_or_rules_db()
        and_rules = self.load_and_rules_db()
        cond_rules = self.load_cond_rules_db()
        self.purchase_rules.update(or_rules)
        self.purchase_rules.update(and_rules)
        self.purchase_rules.update(cond_rules)

        # self.extract_discount_rules()

        highest = 0
        r = None
        for rule_id, rule in self.purchase_rules.items():
            if highest < rule_id:
                highest = rule_id
                r = rule
        num_ids = 0
        if r is not None:
            num_ids = r.number_of_ids()
        self.purchase_rule_ids = highest + 1 + num_ids

    def connect_discount_tree(self, all_connectors: dict[int, IDiscountConnector], all_simple):
        for discount_id, discount in all_connectors.items():
            if discount.children_ids is not None and discount.children_ids != "":
                children_id_list = discount.children_ids.split(",")
                for child_id in children_id_list:
                    if child_id != '':
                        child_id = int(child_id)
                        if child_id in all_connectors.keys():
                            discount.children.append(all_connectors[child_id])
                        else:
                            discount.children.append(all_simple[child_id])

    def connect_discount_to_rules(self, simple, xor):
        # d1.update(d2).update(d3).update(d4).update(d5)
        demi_store = Store(f'{self.name}_discount')
        demi_store.load_my_rules()
        discount_rules = demi_store.purchase_rules

        for id, discount in simple.items():
            if discount.is_rule == 'True':
                discount.rule = discount_rules[discount.rule_id]
        for id, discount in xor.items():
            discount.rule = discount_rules[discount.rule_id]

        Store.delete_record(f'{self.name}_discounts')

    def load_my_discounts(self):

        simple_discounts = SimpleDiscount.load_all_simple_discounts(self.name)
        add_discounts = AddDiscounts.load_all_add_discounts(self.name)
        max_discounts = MaxDiscounts.load_all_max_discounts(self.name)
        or_discounts = OrDiscounts.load_all_or_discounts(self.name)
        xor_discounts = XorDiscounts.load_all_xor_discounts(self.name)

        self.connect_discount_to_rules(simple_discounts, xor_discounts)

        all_connectors = add_discounts
        if max_discounts:
            all_connectors.update(max_discounts)
        if or_discounts:
            all_connectors.update(or_discounts)
        if xor_discounts:
            all_connectors.update(xor_discounts)
        self.connect_discount_tree(all_connectors, simple_discounts)

        # find discount 0:
        self.discounts = add_discounts[0]
        self.discounts.set_db_info(0, self.name)

        self.discount_counter = 0
        for num, discount in chain(simple_discounts.items(), add_discounts.items(), max_discounts.items(),
                                   or_discounts.items(), xor_discounts.items()):
            if num > self.discount_counter:
                self.discount_counter = num
        self.discount_counter += 1

    @staticmethod
    def load_store(store_name):
        return DAL.load(Store, lambda r: r.name == store_name, Store.create_instance_from_db_query)

    @staticmethod
    def load_all_stores():
        out = ConcurrentDictionary()
        for s in DAL.load_all(Store, Store.create_instance_from_db_query):
            out.insert(s.name, s)
            s.load_my_rules()
            s.load_my_discounts()
        return out

    @staticmethod
    def clear_db():
        Product.clear_db()
        DAL.clear(Store)

    @staticmethod
    def add_record(store):
        DAL.add(store)

    @staticmethod
    def delete_record(store_name):
        DAL.delete(Store, lambda r: r.name == store_name)

    @staticmethod
    def number_of_records():
        return DAL.size(Store)

    @staticmethod
    def is_record_exists(store_name):
        return DAL.is_exists(Store, lambda r: r.name == store_name)

    def __str__(self):
        output: str = f'Store: {self.name}\nProducts:\n'
        for i, product in enumerate(self.products):
            output += f'{i}).\t{product.name}. Available quantity: {product.quantity}.\n'
        return output

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def update_product_discounts(self):
        for p in self.products:
            p.discount_price = p.price

        with self.discount_lock:
            for p in self.products:
                self.discounts.set_disconted_price_in_product(p)

    def __dic__(self):
        self.update_product_discounts()
        out = {}
        for p in self.products:
            p_d = p.__dic__()
            p_d["Quantity"] = self.products_quantities.get(p.name).quantity
            if p.name in self.products_with_bid_purchase_policy.keys():
                p_d["isBid"] = self.products_with_bid_purchase_policy.get(p.name).get_cur_bid()
            else:
                p_d["isBid"] = -1
            out[p.name] = p_d

        return out

    def get_name(self):
        return self.name

    def find(self, product_name: str) -> Product | None:
        filtered = list(filter(lambda p: p.name == product_name, self.products))
        return filtered.pop() if len(filtered) > 0 else None

    def contains(self, product_name: str) -> bool:
        return self.find(product_name) is not None

    def add(self, product: Product, quantity: int):
        if quantity > 0:
            if product not in self.products:
                self.products.add(product)
                self.products_quantities.update({product.name: ProductQuantity(quantity)})
                DAL.add(product)
            else:
                new_quantity = self.products_quantities[product.name].refill(quantity)
                if new_quantity > 0:
                    DAL.update(product)
                else:
                    self.remove(product.name)

    def update(self, product_name: str, quantity: int) -> bool:
        p = Product(product_name, self.name)
        is_succeed = p in self.products
        if is_succeed:
            self.products_quantities[product_name].reset(quantity)
            p.quantity = quantity
            DAL.update(p)
        return is_succeed

    def update_db(self, basket):
        for item in basket.items:
            p = self.find(item.product_name)
            p.quantity -= item.quantity
            DAL.update(p)

    def remove(self, product_name: str) -> bool:
        p = Product(product_name, self.name)
        try:
            self.products.remove(p)
            del self.products_quantities[product_name]
            DAL.delete(Product, lambda p: p.name == product_name and p.store_name == self.name)
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
        # TODO:
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
            # remove old product
            q = self.products_quantities[old].quantity
            self.remove(old)
            # insert new product
            new_product = Product(new, self.name, q, product.category, product.price, product.keywords)
            self.add(new_product, q)
        return is_changed

    def change_product_category(self, old: str, new: str) -> bool:
        product = self.find(old)
        is_changed = product is not None
        if is_changed:
            product.category = new
            DAL.update(product)
        return is_changed

    def change_product_price(self, old: float, new: float) -> None:
        for product in filter(lambda p: p.price == old, self.products):
            product.price = new
            DAL.update(product)

    def enforce_purchase_rules(self, basket: Basket) -> Response[bool]:
        for rule in self.purchase_rules:
            res = self.purchase_rules[rule].enforce_rule(basket)
            if not res.success:
                return res
        return report("all rules are kept: Kfir is happy!", True)

    def reserve_products(self, basket: Basket) -> Response[bool]:
        res = self.check_rules(basket)
        if not res.success:
            return res

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
        return Response(is_reservation_succeed)

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

    def check_rules(self, basket: Basket) -> Response[bool]:
        basket.restore_rule_msgs()
        return self.enforce_purchase_rules(basket)

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
        self.purchase_history_str = '#'.join(self.purchase_history)
        DAL.update(self)

    def get_purchase_history(self) -> list[str]:
        return self.purchase_history

    def add_product_to_special_purchase_policy(self, product_name: str, p_policy: IPurchasePolicy) -> Response[bool]:
        if not self.reserve(product_name, 1):
            return report_error("add_product_to_special_purchase_policy",
                                f'cannot reserve product {product_name} for special purchase policy')

        if product_name in self.products_with_special_purchase_policy.keys():
            return report_error("add_product_to_special_purchase_policy",
                                "product can have only 1 special purchase policy")

        self.products_with_special_purchase_policy[product_name] = p_policy
        return report("add_product_to_special_purchase_policy", True)

    def add_product_to_bid_purchase_policy(self, product_name: str, p_policy: IPurchasePolicy) -> \
            Response[bool]:
        if not self.reserve(product_name, 1):
            return report_error("add_product_to_bid_purchase_policy",
                                f'cannot reserve product {product_name} for special purchase policy')

        if product_name in self.products_with_bid_purchase_policy.keys():
            return report_error("add_product_to_bid_purchase_policy", "product can have only 1 special purchase policy")

        self.products_with_bid_purchase_policy[product_name] = p_policy
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

        res = self.products_with_bid_purchase_policy[product_name].approve(person, is_approve)
        if res.success:
            if res.result:
                bid: BidPolicy = self.products_with_bid_purchase_policy.pop(product_name)
                item = Item(product_name, bid.delivery_service.user_name, self.name, 1, bid.highest_bid,
                            bid.highest_bid)
                basket = Basket()
                basket.add_item(item)
                self.add_to_purchase_history(basket)
        return res

    def add_purchase_rule(self, rule: IRule) -> Response:
        with self.purchase_rule_lock:
            self.purchase_rules[self.purchase_rule_ids] = rule
            count = rule.set_db_info(self.name, self.purchase_rule_ids)
            rule.add_to_db()
            self.purchase_rule_ids += count
            return report("add_purchase_rule -> success", rule.rule_id)

    def get_purchase_rules(self):
        return self.purchase_rules

    def remove_purchase_rule(self, rule_id: int):
        rule = self.purchase_rules.pop(rule_id)
        rule.delete_from_db()

    def add_simple_discount(self, percent: int, discount_type: str, rule: IRule = None, discount_for_name=None) -> \
            Response:
        with self.discount_lock:
            discount = SimpleDiscount(self.discount_counter, percent, discount_type, rule, discount_for_name)
            count = discount.set_db_info(self.discount_counter, self.name, rule)
            discount.add_to_db()
            self.discount_counter += (count + 1)
            res = self.discounts.add_discount_to_connector(discount)
            if not res.success:
                return res
            return Response(discount.discount_id, "discount added")

    def connect_discounts(self, id1, id2, connection_type, rule=None) -> Response:
        with self.discount_lock:
            # find
            d1 = self.discounts.find_discount(id1)
            d2 = self.discounts.find_discount(id2)
            if d1 is None or d2 is None:
                return report_error("connecet_discounts", "discount not found")

            # create new connector
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

            if connection_type != "xor":
                conn.add_discount_to_connector(d1, "not")
                conn.add_discount_to_connector(d2, "not")

            # replace 2nd discount with new connector in discount tree
            if self.discounts.replace(id2, conn):
                self.discount_counter += conn.set_db_info(conn.discount_id, self.name)
                conn.add_to_db()
                return report("successfully connected discounts", conn.discount_id)
            else:
                self.discounts.find_discount(id_for_backtrack).add_discount_to_connector(d1)
                return report_error("connect_discounts", "unsuccessful connection of discounts")

    def get_product_obj(self, p_name):
        p_names = [p.name for p in self.products]
        if p_name in p_names:
            return Response(self.find(p_name), "product found")
        else:
            return report_error("get_product_obj", "product doesnt exsist")

    def get_discounts(self) -> list[dict[int:str]]:
        # returns 2 lists: [0]: simple discounts
        #                   [1]: connectors
        d1 = self.discounts.get_all_simple_discounts({})
        d2 = self.discounts.get_all_connectors({})
        return [d1, d2]

    def delete_discount(self, id: int) -> Response:
        if self.discounts.remove_discount(id):
            return report(f"discount {id} has been removeed", True)
        return report_error("delete_discount", f"discount {id} has been removeed")

    def add_owner(self, name: str):
        for key in self.products_with_bid_purchase_policy.keys():
            policy = self.products_with_bid_purchase_policy[key]
            policy.add_to_approval_dict_in_bid_policy(name)

    def remove_owner(self, name: str):
        keys_to_pop = []
        for key in self.products_with_bid_purchase_policy.keys():
            policy = self.products_with_bid_purchase_policy[key]
            policy.remove_from_approval_dict_in_bid_policy(name)
            if policy.is_active == 0:
                keys_to_pop.append(key)
        for key in keys_to_pop:
            self.products_with_bid_purchase_policy.pop(key)

    def get_bid_products(self) -> Response[dict]:
        bids = {}
        for product, bid in self.products_with_bid_purchase_policy.items():
            bids[product] = bid.highest_bid
        return Response(bids)
