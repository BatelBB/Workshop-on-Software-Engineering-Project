from domain.main.bridge.proxy import proxy

import unittest


class TestRegisteredUser(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()
        self.store_was_set = False

    def enter_market(self):
        self.session_id = self.app.enter_market().result

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
        self.store_was_set = True

    def add_items_to_cart(self):
        self.set_stores()
        self.enter_market()
        self.app.register(self.session_id, "user3", "password3")
        self.app.login(self.session_id, "user3", "password3")
        self.app.add_to_cart(self.session_id, "store1", "product1", 3)
        self.app.add_to_cart(self.session_id, "store2", "product2", 5)
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)

    # Use Case: Login
    def test_login(self):
        # happy
        self.app.register(self.session_id, "usr", "password")
        r = self.app.login(self.session_id, "usr", "password")
        self.assertTrue(r.success and r.result, "error: login failed")

        # sad
        r = self.app.login(self.session_id, "notARealUser<:>", "password")
        self.assertFalse(r.success or r.result, "error: successfully login with unregistered username")

        r = self.app.login(self.session_id, "user", "wrongPass")
        self.assertFalse(r.success or r.result, "error: successfully login with invalid password")

        # bad
        self.app.exit_market(self.session_id)
        r = self.app.login(self.session_id, "user", "password")
        self.assertFalse(r.success or r.result, "error: successfully login after exiting market")

    # Use Case: Adding a Product to the Shopping Cart
    def test_items_in_cart_after_logout(self):
        self.add_items_to_cart()

        # happy
        self.enter_market()
        self.app.login(self.session_id, "user3", "password3")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.success and "product1" in cart.result["store1"],
                        "error: product1 not in cart after logout")
        self.assertTrue(cart.success and "product2" in cart.result["store2"],
                        "error: product2 not in cart after logout")
        self.app.logout(self.session_id)

        # sad
        self.app.register(self.session_id, "user4", "password4")
        self.app.login(self.session_id, "user4", "password4")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "user4", "password4")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.success, "error: show cart action failed!")
        self.assertEquals(cart.result, {}, "product1 not in cart")
        self.app.logout(self.session_id)

        # bad
        self.app.login(self.session_id, "user3", "password3")
        self.app.exit_market(self.session_id)
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(not cart.success and cart.result is None, "error: showed cart after exiting the market!")

    # Use Case: Opening a Store
    def test_open_store(self):
        if not self.store_was_set:
            self.set_stores()

        # happy
        self.enter_market()
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue(stores.success, "error: get store action failed!")
        self.assertTrue("store1" in stores.result, "error: store1 not found")
        self.assertTrue("store2" in stores.result, "error: store2 not found")
        products = self.app.get_store_products(self.session_id, "store1")
        self.assertTrue(products.success, "error: get store product action failed!")
        self.assertTrue("product1_1" in products.result, "error: product1_1 not found in store1")
        self.assertTrue("product1_2" in products.result, "error: product1_2 not found in store1")

        # sad
        r = self.app.open_store(self.session_id, "store4")
        self.assertFalse(r.success, "error: a guest has succeeded with opening a store")
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue("store4" not in stores.result, "error: guest created store was found!")

        # bad
        self.app.login(self.session_id, "user1", "password1")
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        r = self.app.open_store(self.session_id, "store5")
        self.assertFalse(r.success, "error: open store action not failed!")
        self.enter_market()
        stores = self.app.get_all_stores(self.session_id)
        self.assertTrue(stores.success and "store5" not in stores.result,
                        "error: store5 is found although created after exiting the market")

