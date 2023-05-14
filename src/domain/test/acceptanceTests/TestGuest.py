from domain.main.bridge.proxy import proxy
import unittest


class TestGuest(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()

    def enter_market(self):
        self.session_id = self.app.enter_market().result

    # Use Case: Entering the system
    def test_enter_market(self):
        r = self.app.enter_market()
        self.assertTrue(r.success, "error entering market: failed to enter!")
        self.assertGreater(self.session_id, -1, "error entering market: got a negative session id!")

    # Use Case: Exiting the system
    def test_exit_market(self):
        self.enter_market()
        r = self.app.exit_market(self.session_id)
        self.assertTrue(r.success and r.result, "error exiting market: action failed!")
        r = self.app.register(self.session_id, "u", "p")
        self.assertFalse(r.success or r.result, "registered after exit_market")

    def setup_2_stores_with_products(self):
        self.enter_market()
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

    # Use Case: Adding a Product to the Shopping Cart
    # Use Case: Inspecting Shopping Cart
    def test_adding_to_cart(self):
        # happy
        self.setup_2_stores_with_products()
        self.set_cart()
        r = self.app.add_to_cart(self.session_id, "store1", "product1_2", 2)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue(cart.success, "error: showing cart action failed")
        self.assertTrue("product1_1" in cart.result["store1"], "error: product1_1 not in cart")
        self.assertTrue("product1_2" in cart.result["store1"], "error: product1_2 not in cart")

        # sad
        r = self.app.add_to_cart(self.session_id, "store2", "product2_1", 50)
        self.assertFalse(r.success or r.result, "error: adding to cart action not failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("store2" not in cart.result.keys() or "product2_1" not in cart.result["store2"],
                        "error: adding more items to cart, more than the store has")

        # bad
        self.app.exit_market(self.session_id)
        r = self.app.add_to_cart(self.session_id, "store1", "product1_2", 2)
        self.assertFalse(r.success or r.result, "error: adding to cart action after exiting market not failed")

    # Use Case: Adding a Product to the Shopping Cart
    # Use Case: Inspecting Shopping Cart
    def test_removing_from_cart(self):
        # happy
        self.set_cart()
        r = self.app.remove_from_cart(self.session_id, "store1", "product1_1")
        self.assertTrue(r.success and r.result, "error: remove product from cart action failed!")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("store1" not in cart.result.keys(), "error: product1_1 didn't removed from cart!")

        # sad
        r = self.app.remove_from_cart(self.session_id, "store1", "product1_2")
        self.assertFalse(r.success or r.result, "error: removing from cart succeeded when there is nothing to remove!")

        # bad
        self.set_cart()
        self.app.exit_market(self.session_id)
        r = self.app.remove_from_cart(self.session_id, "store1", "product1_1")
        self.assertFalse(r.success or r.result, "error: removing from cart succeeded after exiting the market!")

    # todo: add sad, bad tests, add more store and product tests
    # Use Case: Searching for a Product
    def test_product_info(self):
        # happy
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "store1")
        self.assertTrue(products.success, "error: get store products action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        self.assertTrue("product1_2" in products.result, "error: product1_2 did not receive")
        self.assertTrue("product2_1" in products.result, "error: product2_1 did not receive")
        self.assertTrue("product2_2" in products.result, "error: product2_2 did not receive")
        products = self.app.get_products_by_name(self.session_id, "product1_1")
        self.assertTrue(products.success, "error: get product by name action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.get_products_by_category(self.session_id, "cat1")
        self.assertTrue(products.success, "error: get product by category action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.get_products_by_keyword(self.session_id, "car1")
        self.assertTrue(products.success, "error: get product by keyword action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.filter_products_by_price_range(self.session_id, 10, 16)
        self.assertTrue(products.success, "error: filter product by price action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.filter_products_by_rating(self.session_id, 0, 100)
        self.assertTrue(products.success, "error: filter product by rating action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.filter_products_by_category(self.session_id, "cat1")
        self.assertTrue(products.success, "error: filter product by category action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")
        products = self.app.filter_products_by_store_rating(self.session_id, 0, 100)
        self.assertTrue(products.success, "error: filter product by name action failed")
        self.assertTrue("product1_1" in products.result, "error: product1_1 did not receive")

    # Use Case: Purchase Shopping Cart
    def test_product_purchase(self):
        # happy
        self.set_cart()
        r = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/2025", "zambabir", "010101")
        self.assertTrue(r.success and r.result, "error: cart payment with card failed")
        cart = self.app.show_cart(self.session_id)
        self.assertEquals(cart.result, {}, "error: cart not empty after purchase!")
        self.app.exit_market(self.session_id)

        self.set_cart()
        r = self.app.buy_cart_with_paypal(self.session_id, "user-xyz", "123", "zambabir", "010101")
        self.assertTrue(r.success and r.result, "error: cart payment with paypal failed")
        cart = self.app.show_cart(self.session_id)
        self.assertEquals(cart.result, {}, "error: cart not empty after purchase!")

        # sad - bad credit card
        self.app.exit_market(self.session_id)
        self.set_cart()
        r = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/1800", "zambabir", "010101")
        self.assertFalse(r.success or r.result, "error: cart payment with outdated card not failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("product1_1" in cart.result["store1"], "error: product1_1 not in cart after failed purchase "
                                                               "with card!")

        self.app.exit_market(self.session_id)
        self.set_cart()
        r = self.app.buy_cart_with_paypal(self.session_id, "embedded_invalid_user", "123", "zambabir", "010101")
        self.assertFalse(r.success or r.result, "error: cart payment with invalid paypal account not failed")
        cart = self.app.show_cart(self.session_id)
        self.assertTrue("product1_1" in cart.result["store1"], "error: product1_1 not in cart after failed purchase "
                                                               "with paypal!")

        # bad
        self.app.exit_market(self.session_id)
        r = self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/2025", "zambabir", "010101")
        self.assertFalse(r.success or r.success, "error: payment succeeded after exiting market")
        r = self.app.buy_cart_with_paypal(self.session_id, "user856", "123", "zambabir", "010101")
        self.assertFalse(r.success or r.result, "error: cart payment with after exiting the market "
                                                "with paypal account not failed")

    # Use Case: Inspecting Shopping Cart
    def test_losing_cart(self):
        self.set_cart()
        self.app.exit_market(self.session_id)
        self.enter_market()
        cart = self.app.show_cart(self.session_id)
        self.assertEquals(cart.result, {}, "error: cart not empty after a guest exiting and entering the market")

    # Use Case: Registering
    def test_register(self):
        # happy
        self.enter_market()
        r = self.app.register(self.session_id, "user", "password")
        self.assertTrue(r.success and r.result, "error: registering failed")
        r = self.app.register(self.session_id, "user2", "password2")
        self.assertTrue(r.success and r.result, "error: registering failed")

        # sad
        r = self.app.register(self.session_id, "user", "password")
        self.assertFalse(r.success or r.result, "error: successfully registered with an already taken username")
        self.app.exit_market(self.session_id)
        self.enter_market()
        r = self.app.register(self.session_id, "user", "password")
        self.assertFalse(r.success or r.result, "error: successfully registered with an already taken username")

        # bad
        self.app.exit_market(self.session_id)
        r = self.app.register(self.session_id, "user3", "password3")
        self.assertFalse(r.success or r.result, "error: successfully registered after exiting market")



