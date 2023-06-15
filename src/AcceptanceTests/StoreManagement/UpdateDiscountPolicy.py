from Service.bridge.proxy import Proxy
import unittest


class Login(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.happy_user1 = ("usr1", "password")
        cls.happy_user2 = ("usr2", "password")
        cls.happy_user3 = ("usr3", "45sdfgs#$%1")
        cls.not_registered_user = ("usr4", "45sdfgs#$%1")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.happy_user1)
        self.app.register(*self.happy_user2)
        self.app.register(*self.happy_user3)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_add_simple_discount_product(self):
    def test_add_simple_discount_store(self):
    def test_add_simple_discount_category(self):
    def test_connect_product_discounts(self):
    def test_connect_store_discounts(self):
    def test_connect_product_and_store_discounts(self):
    def test_xor_discounts(self):
    def test_max_discounts(self):
    def test_or_discounts(self):
    def test_add_discounts(self):
    def test_3_levels_discount(self):