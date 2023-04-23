from dev.src.main.Utils.Response import Response
from dev.src.main.bridge.proxy import proxy
import unittest


class TestGuest(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def test_enter_market(self):
        self.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

    def test_exit_market(self):
        self.enter_market()
        self.app.exit_market(self.session_id)
        res = self.app.register(self.session_id, "u", "p")
        self.assertFalse(res.success, "registered after exit_market")

    def setup_2_stores_with_products(self):
        self.session_id = self.app.enter_market()
        self.app.register(self.session_id, "user1", "password1")
        self.app.login(self.session_id, "user1", "password1")
        self.app.open_store(self.session_id, "store1")
        self.app.add_product(self.session_id, "store1", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "store1", "product1_2", "cat2", 16, 9, ["cat2", "p2"])

        self.app.enter_market()
        self.app.register(self.session_id, "user2", "password2")
        self.app.login(self.session_id, "user2", "password2")
        self.app.open_store(self.session_id, "store2")
        self.app.add_product(self.session_id, "store2", "product2_1", "cat1", 24, 18, ["car1", "p1"])
        self.app.add_product(self.session_id, "store2", "product2_2", "cat2", 6, 5, ["cat2", "p2"])
        self.app.exit_market(self.session_id)

    def set_cart(self):
        self.enter_market()
        self.app.add_to_cart(self.session_id, "store1", "product1_1", 3)

    def test_adding_to_cart(self):
        # happy
        self.setup_2_stores_with_products()
        self.set_cart()
        res = self.app.add_to_cart(self.session_id, "store1", "product1_2", 2)
        self.assertTrue(res, "add to cart failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(res.success, "action failed")
        self.assertTrue("product1_1" in cart.result["store1"], "product1_1 not in cart")
        self.assertTrue("product1_2" in cart.result["store1"], "product1_2 not in cart")

        # sad
        res2 = self.app.add_to_cart(self.session_id, "store2", "product2_1", 50)
        self.assertFalse(res2.success, "add more items than the store has")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("store2" not in cart.result.keys() or "product2_1" not in cart.result["store2"],
                        "product2_1 in cart")

        # bad
        self.app.exit_market(self.session_id)
        res = self.app.add_to_cart(self.session_id, "store1", "product1_2", 2)
        self.assertFalse(res, "add to cart not failed")

    def test_removing_from_cart(self):
        # happy
        self.set_cart()
        self.app.remove_from_cart(self.session_id, "store1", "product1_1")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.success, "removing failed")
        self.assertTrue("store1" not in cart.result.keys(), "product1_1 didn't removed")

        # sad
        res = self.app.remove_from_cart(self.session_id, "store1", "product1_2")
        self.assertFalse(res.success, "removing succeeded")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.result == {}, "product removed")

    def test_product_info(self):
        # happy
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "store1")
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        self.assertTrue("product1_2" in products.result, "product1_2 did not receive")
        self.assertTrue("product2_1" in products.result, "product2_1 did not receive")
        self.assertTrue("product2_2" in products.result, "product2_2 did not receive")
        products = self.app.get_products_by_name(self.session_id, "product1_1")
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        products = self.app.get_products_by_category(self.session_id, "cat1")
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        products = self.app.get_products_by_keyword(self.session_id, "car1")
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        products = self.app.filter_products_by_price_range(self.session_id, 10, 16)
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        products = self.app.filter_products_by_rating(self.session_id, 0, 100)
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")
        self.assertTrue(products.success, "action failed")
        products = self.app.filter_products_by_store_rating(self.session_id, 0, 100)
        self.assertTrue(products.success, "action failed")
        self.assertTrue("product1_1" in products.result, "product1_1 did not receive")

    def test_product_purchase(self):
        # happy
        self.enter_market()
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "store1", "product1_2", 3)
        res = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/2025")
        self.assertTrue(res.success, "payment failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.result == {}, "cart not empty")
        #todo delivery service check

        # sad - bad credit card
        self.app.exit_market(self.session_id)
        self.set_cart()
        res = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/1800")
        self.assertFalse(res.success, "payment not failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("product1_1" in cart.result["store1"], "product1_1 not in cart")

        # bad
        self.app.exit_market(self.session_id)
        res = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/1800")
        self.assertFalse(res.success, "payment not failed")

    def test_losing_cart(self):
        self.set_cart()
        self.app.exit_market(self.session_id)
        self.enter_market()
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.result == {}, "cart not empty")

    def test_register(self):
        self.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

        # happy
        res = self.app.register(self.session_id, "user", "password")
        self.assertTrue(res.success, "register failed")

        # sad
        s2 = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")
        self.assertNotEqual(s2, self.session_id, f'same session id for 2 users: s2: {s2}      s1:{self.session_id}')

        res1 = self.app.register(self.session_id, "user", "password2")
        self.assertFalse(res1.success, "successfully registered with already taken username")

        # bad
        self.app.exit_market(self.session_id)
        res2 = self.app.register(self.session_id, "user", "password")
        self.assertFalse(res2.success, "successfully registered after exiting market")

    def test_login(self):
        # happy
        self.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

        res = self.app.register(self.session_id, "user", "password")
        self.assertTrue(res.success, "register failed")

        # sad
        res = self.app.login(self.session_id, "notARealUser", "password")
        self.assertFalse(res.success, "successfully login with invalid username")

        res = self.app.login(self.session_id, "user", "password1")
        self.assertFalse(res.success, "successfully login with invalid password")

        # bad
        exit_stat = self.app.exit_market(self.session_id)
        self.assertTrue(exit_stat, "not exited successfully")

        res = self.app.login(self.session_id, "user", "password")
        self.assertFalse(res.success, "logged in after exit")

