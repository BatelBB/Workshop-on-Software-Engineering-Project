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

    def test_adding_to_cart(self):
        stores = self.app.get_all_stores()

    # def test_losing_cart(self):
    #     ...



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

