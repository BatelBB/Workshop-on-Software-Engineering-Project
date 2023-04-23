from dev.src.main.bridge.proxy import proxy
import unittest


class TestStoreManager(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()
        self.enter_market()
        self.app.register(self.session_id, "manager01", "pass1")
        self.app.register(self.session_id, "owner01", "pass1")
        self.app.register(self.session_id, "founder1", "pass1")
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.open_store(self.session_id, "bakery01")
        self.app.open_store(self.session_id, "bakery012")
        self.app.appoint_manager(self.session_id, "bakery01", "manager01")
        self.app.appoint_owner(self.session_id, "bakery01", "owner01")
        self.app.add_product(self.session_id, "bakery01", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery01", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery01", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery01", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)

    def set_stock_permissions(self, cond: bool):
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.set_stock_permission(self.session_id, "manager01", "bakery01", cond)
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager01", "pass1")

    def set_personal_permission(self, cond: bool):
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.set_personal_permissions(self.session_id, "manager01", "bakery01", cond)
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager01", "pass1")

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def test_get_store_purchase_history(self):
        # allowed when appointed and when has a stock permissions
        # happy
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.remove_product(self.session_id, "bakery01", "product1_1")
        self.app.change_product_price(self.session_id, "bakery01", "product1_2", 20)
        self.app.change_product_name(self.session_id, "bakery01", "product1_2", "new_name")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager01", "pass1")
        res = self.app.get_store_purchase_history(self.session_id, "bakery01")
        print(res.result)
        self.assertTrue(("product1_1", 15) in res.result, "product1_1 removed and no longer in purchase history")
        self.assertTrue(("product1_2", 9) in res.result, "product1_2 changed and also changed in purchase history")

        # sad
        res = self.app.get_store_purchase_history(self.session_id, "bakery012")
        self.assertFalse(res.success, "got purchase history of another store")

        self.set_stock_permissions(False)
        res = self.app.get_store_purchase_history(self.session_id, "bakery01")
        self.assertFalse(res.success, "got purchase history without permission")

        # bad
        self.set_stock_permissions(True)
        self.app.exit_market(self.session_id)
        res = self.app.get_store_purchase_history(self.session_id, "bakery01")
        self.assertFalse(res.success, "got purchase history when exited the market")

    def test_add_products_to_store(self):
        # allowed when appointed and when has a stock permissions
        # happy
        self.app.login(self.session_id, "manager01", "pass1")
        self.app.add_product(self.session_id, "bakery01", "pita", "bread", 10, 15, ["bread", "b1"])
        self.app.add_product(self.session_id, "bakery01", "borekas", "bread", 5, 30, ["bread", "b2"])
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("pita" and "borekas" in products.result, "pita and borekas not found")

        # sad
        self.set_stock_permissions(False)
        res = self.app.add_product(self.session_id, "bakery01", "laffa", "bread", 10, 15, ["bread", "b1"])
        self.assertFalse(res.success, "adding product with no permission")
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("laffa" not in products, "laffa found")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        self.enter_market()
        self.app.add_product(self.session_id, "bakery01", "cake3", "bread", 5, 5, ["bread", "b3"])
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("cake3" not in products, "cake3 found")
        self.app.exit_market()

    def test_change_product(self):
        # allowed when appointed and when has a stock permissions
        # happy
        self.enter_market()
        self.app.login(self.session_id, "manager01", "pass1")
        self.app.change_product_name(self.session_id, "bakery01", "pita", "new_pita")
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("new_pita" in products.result, "new_pita not found")
        self.assertTrue("pita" not in products.result, "pita found")

        self.app.change_product_price(self.session_id, "bakery01", "new_pita", 20)
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue(("new_pita", 20) in products.result, "new_pita price didn't change")
        self.assertTrue(("new_pita", 10) not in products.result, "new_pita old price exist")

        # sad
        self.set_stock_permissions(False)
        res = self.app.change_product_price(self.session_id, "bakery01", "new_pita", -5)
        self.assertFalse(res.success, "price changed to negative successfully")
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue(("new_pita", 20) in products.result, "new_pita price change")
        self.assertTrue(("new_pita", -5) not in products.result, "new_pita price changed")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.change_product_price(self.session_id, "bakery01", "new_pita", 10)
        self.assertFalse(res.success, "price changed")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue(("new_pita", 20) in products.result, "new_pita price change")
        self.assertTrue(("new_pita", 10) not in products.result, "new_pita price changed")

    def test_remove_product_from_store(self):
        # allowed when appointed and when has a stock permissions
        # happy
        self.enter_market()
        self.app.login(self.session_id, "owner", "pass1")
        res = self.app.remove_product(self.session_id, "bakery01", "new_pita")
        self.assertTrue(res.success, "product remove fails")
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("new_pita" not in products.result, "new_pita found")

        # sad
        self.set_stock_permissions(False)
        res = self.app.remove_product(self.session_id, "bakery01", "borekas123")
        self.assertFalse(res.success, "product remove succeeded")
        res = self.app.remove_product(self.session_id, "bakery01123", "borekas")
        self.assertFalse(res.success, "product remove succeeded")
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("borekas" in products.result, "borekas not found")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.remove_product(self.session_id, "bakery01", "borekas")
        self.assertFalse(res.success, "product remove succeeded")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery01")
        self.assertTrue("borekas" not in products.result, "borekas found")
        self.app.exit_market(self.session_id)
        
    def test_get_store_personal(self):
        # allowed when has a personal permissions
        # happy
        self.enter_market()
        self.set_personal_permission(True)
        self.app.login(self.session_id, "manager01", "pass1")
        res = self.app.get_store_personal(self.session_id, "bakery01")
        self.assertTrue("owner01" in res.result, "owner01 not in personal list")
        self.assertTrue("founder1" in res.result, "founder1 not in personal list")
        self.assertTrue("manager01" in res.result, "manager01 not in personal list")

        # sad
        self.set_personal_permission(False)
        res = self.app.get_store_personal(self.session_id, "bakery01")
        self.assertFalse(res.success, "can see stores personal without permission")

        # bad
        self.set_personal_permission(True)
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.get_store_personal(self.session_id, "bakery01")
        self.assertFalse(res.success, "got personal list after exit market")