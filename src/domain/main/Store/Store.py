import threading

from src.domain.main.ExternalServices.Provision.IProvisionService import provisionProxy
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService, provisionService
from src.domain.main.Store.Product import Product
from src.domain.main.User.Basket import Basket
from src.domain.main.Utils.Logger import report_info, report_error
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

    def refill(self, additional_quantity: int) -> None:
        with self.lock:
            self.quantity += additional_quantity


class Store:
    # TODO: should be initialized with IPurchasePolicy, IDiscountPolicy
    def __init__(self, name: str):
        self.name = name
        self.products: list[Product] = list()
        self.products_quantities: dict[str, ProductQuantity] = dict()
        self.purchase_history : list[str] = list()
        self.provisionService: IProvisionService = provisionService()
        self.personal: list[str] = []

    def __str__(self):
        output: str = f'#####################\nStore: {self.name}\nProducts:\n'
        for i, product in enumerate(self.products):
            output += f'{i}).\t{product.name}. Available quantity: {self.products_quantities[product.name].quantity}.\n'
        output += '#####################'
        return output

    def __dic__(self):
        dict = {}
        for p in self.products:
            p_d = p.__dic__()
            p_d["Quantity"] = self.products_quantities.get(p.name).quantity
            dict[p.name] = p_d
        return dict

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def contains(self, product: Product) -> bool:
        return product in self.products

    def contains_product(self, product_name: str) -> bool:
        p = Product(product_name)
        return p in self.products

    def get_name(self):
        return self.name

    def order_product(self, product_name: str, quantity: int) -> Response[bool]:
        if self.provisionService.getDelivery(product_name, quantity):
            return report_info("order_product", f'store: {self.name} got delivery of {quantity} {product_name}')
        return report_error("order_product", f'store: {self.name} delivery of {quantity} {product_name} failed!!')

    def add(self, product: Product, quantity: int) -> Response[bool]:
        if not self.contains(product):
            self.products.append(product)

            delivery_response = self.order_product(product.name, quantity)
            if not delivery_response.success:
                return delivery_response

            self.products_quantities.update({product.name: ProductQuantity(quantity)})
            return report_info(self.add.__qualname__, f'{product}, is added to Store \'{self.name}\' successfully!.')
        else:
            return report_error(self.add.__qualname__,
                                f'Store \'{self.name}\' already contains Product \'{product.name}\'')

    def update(self, product_name: str, quantity: int) -> Response[bool]:
        p = Product(product_name)
        if self.contains(p):
            if quantity > 0:
                delivery_response = self.order_product(product_name, quantity)
                if not delivery_response.success:
                    return delivery_response

            self.products_quantities[product_name].refill(quantity)
            return report_info(self.update.__qualname__, f'Store \'{self.name}\': Product \'{product_name}\' quantity '
                                                         f'added {quantity}.')
        else:
            return report_error(self.update.__qualname__,
                                f'Store \'{self.name}\' does not contains Product \'{product_name}\'')

    def remove(self, product_name: str) -> Response[bool]:
        p = Product(product_name)
        if self.contains(p):
            self.products.remove(p)
            del self.products_quantities[product_name]
            return report_info(self.remove.__qualname__, f'Store \'{self.name}\': removed Product \'{product_name}\'.')
        else:
            return report_error(self.remove.__qualname__,
                                f'Store \'{self.name}\' does not contains Product \'{product_name}\'')

    def get_product_price(self, product_name: str) -> float:
        product = Product(product_name)
        product_index = self.products.index(product)
        return self.products[product_index].price

    def reserve(self, product_name: str, quantity: int) -> bool:
        return self.products_quantities[product_name].reserve(quantity)

    def refill(self, reserved: dict[str, int]) -> None:
        for product_name, reserved_quantity in reserved.items():
            self.products_quantities[product_name].refill(reserved_quantity)

    def reserve_products(self, basket: Basket) -> bool:
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

    def calculate_basket_price(self, basket: Basket) -> float:
        price = 0
        # only call from right after reserve
        for item in basket.items:
            price += self.get_product_price(item.product_name)
        return price

    def change_product_name(self, product_old_name: str, product_new_name:str) -> Response[bool]:
        products = self.get_products_by_name(product_old_name)
        for product in products:
            product.set_name(product_new_name)
            self.products_quantities[product_new_name] = self.products_quantities.pop(product_old_name)
        return report_info(self.change_product_name.__qualname__, f'Changed {product_old_name} to {product_new_name} '
                                                                  f'successfully!')

    def change_product_price(self, product_old_price: float, product_new_price:float) -> Response[bool]:
        products = self.get_products_by_price(product_old_price)
        for product in products:
            product.set_price(product_new_price)
        return report_info(self.change_product_price.__qualname__, f'Changed {product_old_price} to {product_new_price} '
                                                                  f'successfully!')

    def add_to_purchase_history(self, baskets: Basket):
        self.purchase_history.append(baskets.__str__())

    def get_purchase_history(self) -> str:
        output = "Purchase history:\n"
        for item in self.purchase_history:
            output += f'{item}\n'
        return output

    def add_personal(self, name: str):
        self.personal.append(name)

    def remove_personal(self, name: str):
        self.personal.remove(name)

    def get_personal(self) -> Response[str]:
        report_info("get_personal", self.personal.__str__())
        return Response(self.personal.__str__())

    # def filter_products_in_price_range(self, products: list[Product] ,min: float, max: float) -> list[Product]:
    #     return self.get_products(lambda p: min <= p.price <= max)
    #
    # def get_products_by_rate(self, min_rate: float) -> list[Product]:
    #     return self.get_products(lambda p: min_rate <= p.rate or p.is_unrated())
    # def pay_for_cart(self, price: float, payment_method: str) -> Response[bool]:
    #     payment = self.payment_factory.getPaymentService(payment_method)
    #     if payment.pay(price):
    #         return report_info(self.pay_for_cart.__qualname__, "Payment successful!")

