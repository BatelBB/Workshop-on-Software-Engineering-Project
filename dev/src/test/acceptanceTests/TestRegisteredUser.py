from dev.src.main.bridge.proxy import proxy

import unittest


class TestRegisteredUser(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def set_stores(self):
        self.enter_market()
        self.app.register(self.session_id, "user1", "password1")
        self.app.login(self.session_id, "user1", "password1")
        self.app.open_store(self.session_id, "store1")
        self.app.add_product(self.session_id, "store1", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "store1", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)

        self.app.register(self.session_id, "user2", "password2")
        self.app.login(self.session_id, "user2", "password2")
        self.app.open_store(self.session_id, "store2")
        self.app.add_product(self.session_id, "store2", "product2_2", "cat2", 6, 5, ["cat2", "p2"])
        self.app.add_product(self.session_id, "store2", "product2_1", "cat1", 24, 18, ["car1", "p1"])
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)

    def add_items_to_cart(self):
        self.set_stores()
        self.enter_market()
        self.app.register(self.session_id, "user3", "password3")
        self.app.login(self.session_id, "user3", "password3")
        self.app.add_to_cart(self.session_id, "store1", "product1", 3)
        self.app.add_to_cart(self.session_id, "store2", "product2", 5)

    def test_logout(self):
        self.add_items_to_cart()
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)

        # happy
        self.enter_market()
        self.app.login(self.session_id, "user3", "password3")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(("product1", 3) in cart, "product1 not in cart")
        self.assertTrue(("product2", 5) in cart, "product2 not in cart")
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)

        # sad
        self.enter_market()
        res = self.app.logout(self.session_id)
        self.assertFalse(res)

        self.app.register(self.session_id, "user4", "password4")
        self.app.login(self.session_id, "user4", "password4")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(len(cart) == 0, "product1 not in cart")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res2 = self.app.logout(self.session_id)
        self.assertFalse(res2)

    def test_open_store(self):
        # happy
        self.enter_market()
        stores = self.app.get_all_stores(self.session_id)

        self.assertTrue("store1" in stores, "store1 not found")
        self.assertTrue("store2" in stores, "store2 not found")
        # products = self.app.get_store_products("store1")
        # self.assertTrue("product1" in products, "product1 not found")

        # sad
        self.enter_market()
        res2 = self.app.open_store(self.session_id, "store4")
        self.assertFalse(res2)
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue("store4" not in stores, "store4 is found")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res2 = self.app.open_store(self.session_id, "store5")
        self.assertFalse(res2)
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue("store5" not in stores, "store5 is found")

