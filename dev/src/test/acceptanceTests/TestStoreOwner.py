from dev.src.main.bridge.proxy import proxy
import unittest


class TestStoreOwner(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()
        self.enter_market()
        self.app.register(self.session_id, "owner", "pass1")
        self.app.register(self.session_id, "founder", "pass1")
        self.app.login(self.session_id, "founder", "pass1")
        self.app.open_store(self.session_id, "bakery")
        self.app.appoint_owner(self.session_id, "bakery", "owner")
        self.app.logout(self.session_id)

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def test_add_products_to_store(self):
        # happy
        self.app.login(self.session_id, "owner", "pass1")
        self.app.add_product(self.session_id, "bakery", "pita", "bread", 10, 15, ["bread", "b1"])
        self.app.add_product(self.session_id, "bakery", "borekas", "bread", 5, 30, ["bread", "b2"])
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("pita" and "borekas" in products, "pita and borekas not found")

        # sad
        self.app.add_product(self.session_id, "bakery", "cake1", "bread", 5, -5, ["bread", "b3"])
        self.app.add_product(self.session_id, "bakery", "cake2", "bread", -5, 5, ["bread", "b3"])
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("cake1" not in products, "cake1 found")
        self.assertTrue("cake2" not in products, "cake2 found")

        # bad
        self.app.logout(self.session_id)
        self.app.add_product(self.session_id, "bakery", "cake3", "bread", 5, 5, ["bread", "b3"])
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("cake3" not in products, "cake3 found")
        self.app.exit_market(self.session_id)
        self.app.add_product(self.session_id, "bakery", "cake4", "bread", 5, 5, ["bread", "b3"])
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("cake4" not in products, "cake4 found")

    def test_change_product(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "owner", "pass1")
        self.app.change_product_name(self.session_id, "bakery", "pita", "new_pita")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("new_pita" in products, "new_pita not found")
        self.assertTrue("pita" not in products, "pita found")

        self.app.change_product_price(self.session_id, "bakery", "new_pita", 20)
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue(("new_pita", 20) in products, "new_pita price didn't change")
        self.assertTrue(("new_pita", 10) not in products, "new_pita old price exist")

        # sad
        res = self.app.change_product_price(self.session_id, "bakery", "new_pita", -5)
        self.assertFalse(res, "price changed to negative successfully")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue(("new_pita", 20) in products, "new_pita price change")
        self.assertTrue(("new_pita", -5) not in products, "new_pita price changed")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.change_product_price(self.session_id, "bakery", "new_pita", 10)
        self.assertFalse(res, "price changed")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue(("new_pita", 20) in products, "new_pita price change")
        self.assertTrue(("new_pita", 10) not in products, "new_pita price changed")

    def test_remove_product_from_store(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "owner", "pass1")
        self.app.remove_product(self.session_id, "bakery", "new_pita")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("new_pita" not in products, "new_pita found")

        # sad
        self.app.remove_product(self.session_id, "bakery", "borekas123")
        self.app.remove_product(self.session_id, "bakery123", "borekas")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("borekas" in products, "borekas not found")

        # bad
        self.app.logout(self.session_id)
        self.app.remove_product(self.session_id, "bakery", "borekas")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("borekas" not in products, "borekas found")
        self.app.exit_market(self.session_id)
        self.app.remove_product(self.session_id, "bakery", "borekas")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("borekas" not in products, "borekas found")

    def test_add_manager(self):
        # happy
        self.enter_market()
        self.app.register(self.session_id, "manager1", "pass1")
        self.app.login(self.session_id, "owner", "pass1")
        res = self.app.appoint_manager(self.session_id, "bakery", "manager1")
        self.assertTrue(res, "manager1 appointment failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("manager1" in res2, "manager1 not in personal list")

        # sad
        res = self.app.appoint_manager(self.session_id, "bakery", "u6")
        self.assertFalse(res, "unregistered user appointment not failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse("u6" in res2, "u6 in personal list")

        res = self.app.appoint_manager(self.session_id, "bakery", "u6")
        self.assertFalse(res, "unregistered user appointment not failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse("u6" in res2, "u6 in personal list")

        # bad
        self.app.register(self.session_id, "manager2", "pass1")
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.appoint_manager(self.session_id, "bakery", "manager2")
        self.assertFalse(res, "manager appointment succeeded")
        self.enter_market()
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("manager2" not in res2, "manager2 in personal list")

    def test_add_owner(self):
        # happy
        self.app.register(self.session_id, "owner2", "pass1")
        self.app.login(self.session_id, "owner", "pass1")
        res = self.app.appoint_owner(self.session_id, "bakery", "owner2")
        self.assertTrue(res, "manager appointment failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("owner2" in res2, "owner2 not in personal list")

        # sad
        res = self.app.appoint_owner(self.session_id, "bakery", "owner5")
        self.assertFalse(res, "unregistered user appointment not failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse("owner5" in res2, "owner5 in personal list")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "owner2", "pass1")
        res = self.app.appoint_owner(self.session_id, "bakery", "owner")
        self.assertFalse(res, "a circular owner appointment")

        # bad
        self.app.register(self.session_id, "owner3", "pass1")
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.appoint_owner(self.session_id, "bakery", "owner3")
        self.assertFalse(res, "owner appointment not failed")
        self.enter_market()
        self.app.login(self.session_id, "owner", "pass1")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("owner3" not in res2, "owner3 in personal list")
        self.app.logout(self.session_id)

    def test_purchase_history(self):
        self.app.login(self.session_id, "owner", "pass1")
        self.app.add_product(self.session_id, "bakery", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "owner", "pass1")
        self.app.remove_product(self.session_id, "bakery", "product1_1")
        self.app.change_product_price(self.session_id, "bakery", "product1_2", 20)
        self.app.change_product_name(self.session_id, "bakery", "product1_2", "new_name")
        res = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertTrue(("product1_1", 15) in res, "product1_1 removed and no longer in purchase history")
        self.assertTrue(("product1_2", 9) in res, "product1_2 changed and also changed in purchase history")


