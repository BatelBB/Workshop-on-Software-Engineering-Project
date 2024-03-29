from functools import reduce

from sqlalchemy import Column, ForeignKey, String, Integer, Float

from DataLayer.DAL import DAL, Base


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'extend_existing': True}
    product_name = Column(String, primary_key=True)
    store_name = Column(String, primary_key=True)
    username = Column(String, ForeignKey('users.username'), primary_key=True)
    quantity = Column(Integer)
    price = Column(Float)
    discount_price = Column(Float)

    def __init__(self, product_name: str, username: str, store_name: str, quantity: int = 0, price: float = 0.0,
                 discount_price: float = 0.00):
        self.product_name = product_name
        self.username = username
        self.store_name = store_name
        self.quantity = quantity
        self.price = price
        self.discount_price = price
        self.rule_msg = ""

    @staticmethod
    def create_instance_from_db_query(r):
        return Item(r.product_name, r.username, r.store_name, r.quantity, r.price, r.discount_price)

    def __str__(self):
        return f'Product: \'{self.product_name}\', Quantity: {self.quantity}, Price: {self.price}, Discount-Price: {self.discount_price}'

    def __dic__(self) -> dict:
        return {"Quantity": self.quantity, "Price": self.price}

    def __eq__(self, other):
        return self.product_name == other.product_name

    def get_quantity(self):
        return self.quantity

    def get_name(self):
        return self.product_name

    def get_price(self) -> float:
        return self.price

    @staticmethod
    def load_item(product_name, username, store_name):
        return DAL.load(Item, lambda r: r.username == username and r.store_name == store_name and r.product_name == product_name, Item.create_instance_from_db_query)

    @staticmethod
    def number_of_records():
        return DAL.size(Item)


class Basket:
    def __init__(self):
        self.items: list[Item] = list()

    def __str__(self):
        return reduce(lambda acc, item: acc + '\n' + item.__str__(), self.items, '')

    def __dic__(self):
        output = {}
        for i in self.items:
            output[i.product_name] = i.__dic__()
        return output

    def add_item(self, item: Item) -> int:
        new_quantity = item.quantity

        try:
            item_index = self.items.index(item)
            additional_quantity = item.quantity
            item_in_basket = self.items[item_index]
            new_quantity = item_in_basket.quantity + additional_quantity

            if new_quantity <= 0:
                self.items.remove(item)
            else:
                item.quantity = new_quantity
                item_in_basket.quantity = new_quantity

        except ValueError:
            self.items.append(item)

        DAL.add(item)

        return max(0, new_quantity)

    def remove_item(self, item: Item) -> bool:
        try:
            self.items.remove(item)
            DAL.delete(Item, lambda r: r.username == item.username and r.store_name == item.store_name and r.product_name == r.product_name)
            return True
        except ValueError:
            return False

    def update_item(self, item: Item) -> bool:
        try:
            item_index = self.items.index(item)
            item_in_basket = self.items[item_index]
            item_in_basket.quantity = item.quantity
            DAL.update(item)
            return True
        except ValueError:
            return False

    def get_item(self, name):
        for i in self.items:
            if i.product_name == name:
                return i

    # only call from store
    def calc_price(self) -> float:
        price = 0
        for item in self.items:
            price += item.discount_price * item.quantity
        return price

    def deep_copy(self):
        new_basket = Basket()
        for item in self.items:
            new_item = Item(item.product_name, item.username, item.store_name, item.quantity, item.price)
            new_item.discount_price = item.discount_price
            new_basket.add_item(new_item)
        return new_basket

    def restore_rule_msgs(self):
        for i in self.items:
            i.rule_msg = ""