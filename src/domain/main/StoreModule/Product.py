from typing import Optional

from sqlalchemy import Column, String, ForeignKey, Integer, Float

from DataLayer.DAL import DAL, Base


class Product(Base):

    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True}
    name = Column("name", String, primary_key=True)
    store_name = Column("store_name", String, ForeignKey('stores.name'), primary_key=True)
    quantity = Column("quantity", Integer)
    category = Column("category", String)
    price = Column("price", Float)
    keywords_str = Column("keywords_str", String, default='')
    rate = Column("rate", Integer)

    def __init__(self, name: str, store_name, quantity=1, category: str = "whatever", price: float = 0.0, keywords: Optional[list[str]] = None, rate: int = 5):
        self.rate = rate
        self.name = name
        self.store_name = store_name
        self.quantity = quantity
        self.category = category
        self.price = price
        self.keywords = keywords
        if self.keywords is None:
            self.keywords = []
        self.keywords_str = '#'.join(self.keywords)
        self.keywords.append(name)
        self.discount_price = price

    @staticmethod
    def create_instance_from_db_query(r):
        p = Product(r.name, r.store_name, r.quantity, r.category, r.price, r.keywords_str.split('#'), r.rate)
        try:
            p.keywords.remove('')  # drop default DB value
        except ValueError:
            pass
        return p

    @staticmethod
    def load_products_of(store_name):
        return DAL.load_all_by(Product, lambda r: r.store_name == store_name, Product.create_instance_from_db_query)

    @staticmethod
    def clear_db():
        DAL.clear(Product)

    @staticmethod
    def load_product(product_name, store_name):
        return DAL.load(Product, lambda r: r.name == product_name and r.store_name == store_name, Product.create_instance_from_db_query)

    @staticmethod
    def number_of_records():
        return DAL.size(Product)

    def __str__(self):
        rate: str = 'Not rated yet' if self.is_unrated() else self.rate
        return f'Product \'{self.name}\', Category: \'{self.category}\', Price: {self.price}, Rate: {rate}'

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __dic__(self):
        return {"Name": self.name, "Price": self.price, "Category": self.category, "Rate": self.rate,
                "Keywords": self.keywords_str, "discounted_price": self.discount_price}

    def is_unrated(self):
        return self.rate is None
