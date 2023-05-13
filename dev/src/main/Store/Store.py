import threading

from multipledispatch import dispatch

from dev.src.main.Store.Product import Product
from dev.src.main.User.Basket import Basket
from dev.src.main.Utils.Logger import report_error
from dev.src.main.Utils.Response import Response


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
    # TODO: should be initialized with IPurchasePolicy, IDiscountPolicy
    def __init__(self, name: str):
        self.name = name
        self.products: set[Product] = set()
        self.products_quantities: dict[str, ProductQuantity] = dict()

    def __str__(self):
        output: str = f'Store: {self.name}\nProducts:\n'
        for i, product in enumerate(self.products):
            output += f'{i}).\t{product.name}. Available quantity: {self.products_quantities[product.name].quantity}.\n'
        return output

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def find(self, product_name: str) -> Product | None:
        filtered = list(filter(lambda p: p.name == product_name, self.products))
        return filtered.pop() if len(filtered) > 0 else None

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
        product = self.find(product_name)
        return Response(product) if product is not None else report_error(self.get_product.__qualname__,f'Store \'{self.name}\' does not contains Product \'{product_name}\'')

    def get_all(self) -> set[Product]:
        return self.products

    def amount_of(self, product_name: str) -> int:
        return self.products_quantities[product_name].quantity if product_name in self.products_quantities else 0

    def get_product_price(self, product_name: str) -> float:
        p = self.find(product_name)
        return p.price if p is not None else -1

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

    def get_products_by(self, predicate) -> list[(str, Product)]:
        products = list(filter(predicate, self.products))
        return list(map(lambda p: (self.name, p), products))
