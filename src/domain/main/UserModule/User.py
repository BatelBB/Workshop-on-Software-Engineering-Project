import random
import bcrypt
from domain.main.Utils import Base_db
from domain.main.Utils.Base_db import session_DB
from src.domain.main.Service.IService import IService
from src.domain.main.UserModule.Cart import Cart
from src.domain.main.UserModule.Role.Visitor import Visitor
from src.domain.main.Utils.Response import Response
from sqlalchemy import Column, Integer, String


class User(Base_db.Base):
    __tablename__ = 'users'
    username = Column("username", String, primary_key=True)
    encrypted_password = Column("encrypted_password", String)

    def __init__(self, username: str = "Visitor", encrypted_password: str = "Visitor"):
        self.user_id = None
        self.username = username
        self.encrypted_password = bcrypt.hashpw(bytes(encrypted_password, 'utf8'), bcrypt.gensalt())
        self.is_canceled = False
        self.role = Visitor(self)
        self.cart = Cart()
        self.is_logged_in = False

    def __repr__(self):
        return f"<User(name='{self.username}', email='{self.password}')>"

    def __str__(self):
        return self.role.__str__()

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def register(self) -> Response[bool]:
        self.user_id = random.randint(100000000, 999999999)
        return self.role.register()

    # def is_registered(self) -> bool:
    #     q = session_DB.query(User.username).filter(User.username == self.username)
    #     return session_DB.query(q.exists()).scalar()

    def login(self, encrypted_password: str) -> Response[bool]:
        return self.role.login(encrypted_password)

    def logout(self) -> Response[bool]:
        return self.role.logout()

    def is_member(self) -> bool:
        return self.role.is_member()

    def is_admin(self) -> bool:
        return self.role.is_admin()

    def add_to_cart(self, store_name: str, product_name: str, price: float, quantity: int = 1) -> Response[bool]:
        return self.role.add_to_cart(store_name, product_name, price, quantity)

    def remove_product_from_cart(self, store_name: str, product_name: str) -> Response[bool]:
        return self.role.remove_product_from_cart(store_name, product_name)

    def update_cart_product_quantity(self, store_name: str, product_name: str, quantity: int) -> Response[bool]:
        return self.role.update_cart_product_quantity(store_name, product_name, quantity)

    def show_cart(self) -> Response[dict]:
        return self.role.show_cart()

    def verify_cart_not_empty(self) -> Response[bool]:
        return self.role.verify_cart_not_empty()

    def get_baskets(self) -> dict:
        return self.role.get_baskets()

    def empty_basket(self, store_name: str) -> None:
        self.role.empty_basket(store_name)

    def get_user_id(self) -> int:
        return self.user_id

    @staticmethod
    def is_registered(username: str) -> bool:
        q = session_DB.query(User.username).filter(User.username == username)
        return session_DB.query(q.exists()).scalar()

    @staticmethod
    def clear_db():
        session_DB.query(User).delete()
        session_DB.commit()

    @staticmethod
    def load_user(username: str):
        q = session_DB.query(User).filter(User.username == username).all()
        exist = len(q) > 0
        if exist:
            row = q[0]
            user = User(username=row.username)
            user.encrypted_password = row.encrypted_password
            return user
        return None

