from Service.bridge.proxy import Proxy
import unittest


class Login(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.registered_buyer1 = ("usr2", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_founder1)
        self.app.register(*self.registered_buyer1)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_add_simple_discount_product(self):
        self.app.login(*self.store_founder1)
        r = self.app.add_simple_discount("bakery", "product", 50, "bread")

    def test_add_simple_discount_product(self):
        self.app.login(*self.store_founder1)
        r = self.app.add_simple_discount("bakery", "product", 50, "bread")

    def test_add_simple_discount_store(self):
    def test_add_simple_discount_category(self):
    def test_connect_product_discounts(self):
    def test_connect_store_discounts(self):
    def test_connect_product_and_store_discounts(self):
    def test_xor_discounts(self):
        self.app.connect_discounts("bakery", 1, 2, "xor")#must add rule, if rule == True then 1 only is valid else 2 only valid
    def test_max_discounts(self):
        self.app.connect_discounts("bakery", 1, 2, "max")#choose maximum disc according to basket price after the discount
    def test_or_discounts(self):
        self.app.connect_discounts("bakery", 1, 2, "max")#choose minimum disc according to basket price after the discount
    def test_add_discounts(self):
        self.app.connect_discounts("bakery", 1, 2, "max")#choose both discounts
    def test_3_levels_discount(self):

    def set_store(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()