from typing import Optional

from sqlalchemy import Column, String, ForeignKey, Integer, Float

from src.domain.main.Utils import Base_db
from src.domain.main.Utils.Base_db import session_DB


class Product(Base_db.Base):

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

    @staticmethod
    def load_product(product_name, store_name):
        q = session_DB.query(Product).filter(Product.name == product_name, Product.store_name == store_name).all()
        exist = len(q) > 0
        if exist:
            row = q[0]
            keywords = row.keywords_str.split('#')
            try:
                keywords.remove('') # drop default DB value
            except ValueError:
                pass
            return Product(row.name, row.store_name, row.quantity, row.category, row.price, keywords, row.rate)
        return None

    @staticmethod
    def number_of_records():
        session_DB.flush()
        return session_DB.query(Product).count()


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
