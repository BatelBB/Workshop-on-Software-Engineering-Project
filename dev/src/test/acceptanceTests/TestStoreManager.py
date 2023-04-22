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
        self.app.open_store(self.session_id, "bakery")
        self.app.open_store(self.session_id, "bakery2")
        self.app.appoint_manager(self.session_id, "bakery", "manager01")
        self.app.appoint_owner(self.session_id, "bakery", "owner01")
        self.app.add_product(self.session_id, "bakery", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def test_get_store_personal(self):
        # happy
        self.app.login(self.session_id, "manager01", "pass1")
        res = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("owner01" in res, "owner01 not in personal list")
        self.assertTrue("founder1" in res, "founder1 not in personal list")
        self.assertTrue("manager01" in res, "manager01 not in personal list")

        # sad
        res = self.app.get_store_personal(self.session_id, "bakery2")
        self.assertFalse(res, "can see other stores personal list")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse(res, "got personal list after exit market")

    def test_get_store_purchase_history(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.remove_product(self.session_id, "bakery", "product1_1")
        self.app.change_product_price(self.session_id, "bakery", "product1_2", 20)
        self.app.change_product_name(self.session_id, "bakery", "product1_2", "new_name")
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "manager01", "pass1")
        res = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertTrue(("product1_1", 15) in res, "product1_1 removed and no longer in purchase history")
        self.assertTrue(("product1_2", 9) in res, "product1_2 changed and also changed in purchase history")

        # sad
        res = self.app.get_store_purchase_history(self.session_id, "bakery2")
        self.assertFalse(res, "got purchase history of another store")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        res = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertFalse(res, "got purchase history when exited the market")
