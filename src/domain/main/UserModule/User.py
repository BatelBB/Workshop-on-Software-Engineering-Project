import hashlib
import random
from sqlalchemy import Column, String, Boolean, Text
from DataLayer.DAL import DAL, Base
from src.domain.main.UserModule.Cart import Cart
from src.domain.main.UserModule.Role.Admin import Admin
from src.domain.main.UserModule.Role.Visitor import Visitor
from src.domain.main.Utils.Response import Response


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    username = Column("username", String, primary_key=True)
    encrypted_password = Column("encrypted_password", Text)
    is_admin = Column("is_admin", Boolean)

    def __init__(self, username: str = "Visitor", password: str = "Visitor", is_admin=False):
        self.user_id = None
        self.username = username
        # self.encrypted_password: bytes = bcrypt.hashpw(bytes(password, 'utf8'), bcrypt.gensalt())
        self.encrypted_password = hashlib.sha256(password.encode('utf8')).hexdigest()
        self.is_canceled = False
        self.is_admin = is_admin
        self.role = Admin(self) if is_admin else Visitor(self)
        self.cart = Cart(username)
        self.is_logged_in = False

    @staticmethod
    def create_instance_from_db_query(r):
        user = User(username=r.username, is_admin=r.is_admin)
        user.encrypted_password = r.encrypted_password
        user.cart = Cart.load_cart(r.username)
        return user

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
        return Response(True)

    def login(self, encrypted_password: str) -> bool:
        return self.role.login(encrypted_password)

    def logout(self) -> Response[bool]:
        return self.role.logout()

    def is_member(self) -> bool:
        return self.role.is_member()

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

    def cancel_membership(self):
        self.is_canceled = True
        self.role = Visitor(self)

    @staticmethod
    def is_record_exists(username: str) -> bool:
        return DAL.is_exists(User, lambda u: u.username == username)

    @staticmethod
    def clear_db():
        Cart.clear_db()
        DAL.clear(User)

    @staticmethod
    def load_user(username: str):
        return DAL.load(User, lambda u: u.username == username, User.create_instance_from_db_query)

    @staticmethod
    def add_record(user):
        DAL.add(user)

    @staticmethod
    def number_of_records():
        return DAL.size(User)
