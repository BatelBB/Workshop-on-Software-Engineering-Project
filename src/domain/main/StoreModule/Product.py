from typing import Optional

from sqlalchemy import Column, String, ForeignKey, Integer, Float

from domain.main.Utils import Base_db
from domain.main.Utils.Base_db import session_DB


class Product(Base_db.Base):

    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True}
    name = Column("name", String, primary_key=True)
    store_name = Column("store_name", String, ForeignKey('stores.name'), primary_key=True)
    quantity = Column("quantity", Integer)
    category = Column("category", String)
    price = Column("price", Float)
    keywords_str = Column("keywords_str", String)
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
        self.keywords.append(name)
        self.keywords_str = '#'.join(self.keywords)

    @staticmethod
    def load_products_of(store_name):
        products = []
        records = session_DB.query(Product).filter(Product.store_name == store_name).all()
        for r in records:
            products.append(Product(r.name, r.store_name, r.quantity, r.category, r.price, r.keywords_str.split('#'), r.rate))
        return products

    @staticmethod
    def clear_db():
        session_DB.query(Product).delete()
        session_DB.commit()

    def __str__(self):
        rate: str = 'Not rated yet' if self.is_unrated() else self.rate
        return f'Product \'{self.name}\', Category: \'{self.category}\', Price: {self.price}, Rate: {rate}'

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __dic__(self):
        return {"Name": self.name, "Price": self.price, "Category": self.category, "Rate": self.rate}

    def is_unrated(self):
        return self.rate is None
