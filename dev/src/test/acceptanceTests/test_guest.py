from dev.src.test.acceptanceTests.bridge.Bridge import Bridge
from dev.src.test.acceptanceTests.bridge.proxy import proxy

import unittest


class test_guest(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()

    def test_enter_market(self):
        self.session_id = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

    def test_exit_market(self):
        self.test_enter_market()
        self.app.exit_market(self.session_id)
        res = self.app.register(self.session_id, "u", "p")
        self.assertFalse(res, "registered after exit_market")


    def setup_2_stores_with_products(self):
        self.session_id = self.app.enter_market()
        res1 = self.app.register(self.session_id, "user1", "password1")
        res2 = self.app.login(self.session_id, "user1", "password1")
        res3 = self.app.open_store(self.session_id, "store1")
        res4 = self.app.add_product(self.session_id, "store1", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        res4 = self.app.add_product(self.session_id, "store1", "product1_2", "cat2", 16, 9, ["cat2", "p2"])


        s2 = self.app.enter_market()
        res1 = self.app.register(self.session_id, "user2", "password2")
        res2 = self.app.login(self.session_id, "user2", "password2")
        res3 = self.app.open_store(s2, "store2")
        res4 = self.app.add_product(self.session_id, "store2", "product2_1", "cat1", 24, 18, ["car1", "p1"])
        res4 = self.app.add_product(self.session_id, "store2", "product2_2", "cat2", 6, 5, ["cat2", "p2"])



    def test_adding_to_cart(self):
        self.setup_2_stores_with_products()

        cur_s = self.app.enter_market()
        stores = self.app.get_all_stores()
        store1 = stores[0]
        store2 = stores[1]

        res = self.app.add_to_cart(cur_s, "store1", "product1", 3)
        self.assertTrue(res, "add to cart failed")
        cart = self.app.show_cart(cur_s)
        self.assertTrue(("product1", 3) in cart, "product1 not in cart")

        res2 = self.app.add_to_cart(cur_s, "store2", "product2", 5)
        self.assertTrue(res, "add to cart failed")
        cart = self.app.show_cart(cur_s)
        self.assertTrue(("product1", 3) in cart and ("product2", 5) in cart, "product2 not in cart")





    def test_losing_cart(self):
        ...



    def test_register(self):
        self.session_id = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

        #happy
        res = self.app.register(self.session_id, "user", "password")
        self.assertTrue(res, "register failed")
        # sad
        s2 = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")
        self.assertNotEqual(s2, self.session_id, f'same sessionid for 2 users: s2: {s2}      s1:{self.session_id}')

        res1 = self.app.register(self.session_id, "user", "password2")
        self.assertFalse(res1, "successfully registered with already taken username")

        # bad
        self.app.exit_market(self.session_id)
        res2 = self.app.register(self.session_id, "user", "password")
        self.assertFalse(res2, "successfully registered after exiting market")



    def test_login(self):
        self.session_id = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")

        res = self.app.register(self.session_id, "user", "password")
        self.assertTrue(res, "register failed")

        #sad
        res = self.app.login(self.session_id, "user1", "password")
        self.assertFalse(res, "successfully login with invalid username")

        res = self.app.login(self.session_id, "user", "password1")
        self.assertFalse(res, "successfully login with invalid password")

        #happy
        res = self.app.login(self.session_id, "user", "password")
        self.assertTrue(res, "failed to login")

        #bad
        exit = self.app.exit_market(self.session_id)
        self.assertTrue(exit, "not exited successsfuly")

        res = self.app.login(self.session_id, "user", "password")
        self.assertFalse(res, "loggedin after exit")

