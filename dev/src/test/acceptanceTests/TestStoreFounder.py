from dev.src.main.bridge.proxy import proxy
import unittest


class TestStoreOwner(unittest.TestCase):
    session_id: int
    app: proxy
    store_id: int
    product_ids: list[int]

    def setUp(self) -> None:
        self.app = proxy()
        self.enter_market()
        self.app.register(self.session_id, "u1", "pass1")
        self.app.login(self.session_id, "u1", "pass1")
        self.app.open_store(self.session_id, "bakery")

    def enter_market(self):
        self.session_id = self.app.enter_market()

    def test_add_products_to_store(self):
        # happy
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

    def test_remove_product_from_store(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "u1", "pass1")
        self.app.remove_product(self.session_id, "bakery", "pita")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("pita" not in products, "pita found")

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

    def add_manager(self):
        # happy
        self.app.register(self.session_id, "u2", "pass1")
        self.app.login(self.session_id, "u1", "pass1")
        res = self.app.appoint_manager(self.session_id, "bakery", "u2")
        self.assertTrue(res, "manager appointment failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("u1" in res2, "u1 not in personal list")

        # sad
        res = self.app.appoint_manager(self.session_id, "bakery", "u6")
        self.assertFalse(res, "unregistered user appointment not failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse("u6" in res2, "u6 in personal list")

        # bad
        self.app.register(self.session_id, "u2", "pass1")
        self.app.login(self.session_id, "u1", "pass1")
        res = self.app.appoint_manager(self.session_id, "bakery", "u2")
        self.assertTrue(res, "manager appointment failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("u1" in res2, "u1 not in personal list")

    def add_owner(self):
        # happy
        self.app.register(self.session_id, "u2", "pass1")
        self.app.login(self.session_id, "u1", "pass1")
        res = self.app.appoint_owner(self.session_id, "bakery", "u2")
        self.assertTrue(res, "manager appointment failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("u1" in res2, "u1 not in personal list")

        # sad
        res = self.app.appoint_owner(self.session_id, "bakery", "u6")
        self.assertFalse(res, "unregistered user appointment not failed")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertFalse("u6" in res2, "u6 in personal list")

        self.app.logout(self.session_id)
        self.app.register(self.session_id, "u3", "pass1")
        self.app.login(self.session_id, "u2", "pass1")
        self.app.appoint_owner(self.session_id, "bakery", "u3")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "u3", "pass1")
        res = self.app.appoint_owner(self.session_id, "bakery", "u3")
        self.assertFalse(res, "a circular appointment not failed")
        # res2 = self.app.get_store_personal(self.session_id, "bakery")
        # self.assertFalse("u3" in res2, "u3 in personal list")

        # bad
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "u4", "pass1")
        res = self.app.appoint_owner(self.session_id, "bakery", "u4")
        self.assertFalse(res, "owner appointment not failed")
        self.app.login(self.session_id, "u1", "pass1")
        res2 = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue("u4" not in res2, "u4 in personal list")

    def close_store(self):
        # sad
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "u2", "pass1")
        res = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(res, "not the founder closed the store")

        res = self.app.close_store(self.session_id, "notReal")
        self.assertFalse(res, "closed invalid store")

        # bad
        self.app.logout(self.session_id)
        self.close_store()
        res = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(res, "not the founder closed the store")

        res = self.app.close_store(self.session_id, "notReal")
        self.assertFalse(res, "closed invalid store")

        # happy
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery", "borekas", 3)
        self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/2025")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "u1", "pass1")
        res = self.app.close_store(self.session_id, "bakery")
        self.assertTrue(res, "the founder couldn't close the store")
        res = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertTrue(res, "founder can't watch its store history")
        res = self.app.get_store_personal(self.session_id, "bakery")
        self.assertTrue(len(res) != 0, "founder can't watch its store appointments")
