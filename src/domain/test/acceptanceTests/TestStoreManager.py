from domain.main.bridge.proxy import proxy
import unittest


class TestStoreManager(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()
        self.enter_market()
        self.app.register(self.session_id, "manager5", "pass1")
        self.app.register(self.session_id, "owner5", "pass1")
        self.app.register(self.session_id, "founder3", "pass1")
        self.app.login(self.session_id, "founder3", "pass1")
        self.app.open_store(self.session_id, "bakery3")
        self.app.open_store(self.session_id, "bakery4")
        self.app.appoint_manager(self.session_id, "bakery3", "manager5")
        self.app.appoint_owner(self.session_id, "bakery3", "owner5")
        self.app.add_product(self.session_id, "bakery3", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery3", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery3", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery3", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)
        self.exit_market()

    def set_stock_permissions(self, cond: bool):
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder3", "pass1")
        self.app.set_stock_permission(self.session_id, "manager5", "bakery3", cond)
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager5", "pass1")

    def set_personal_permission(self, cond: bool):
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder3", "pass1")
        self.app.set_personal_permissions(self.session_id, "manager5", "bakery3", cond)
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager5", "pass1")

    def enter_market(self):
        self.session_id = self.app.enter_market().result

    def exit_market(self):
        self.app.exit_market(self.session_id)

    # Use Case: Update store inventory
    def test_add_products_to_store(self):
        # happy
        self.enter_market()
        self.set_stock_permissions(True)
        r = self.app.add_product(self.session_id, "bakery3", "pita", "bread", 10, 15, ["bread", "b1"])
        self.assertTrue(r.success and r.result, "error: add product action failed!")
        r = self.app.add_product(self.session_id, "bakery3", "borekas", "bread", 5, 30, ["bread", "b2"])
        self.assertTrue(r.success and r.result, "error: add product action failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("pita" and "borekas" in products.result, "pita and borekas not found")

        # sad
        r = self.app.add_product(self.session_id, "bakery3", "cake1", "bread", 5, -5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        r = self.app.add_product(self.session_id, "bakery3", "cake2", "bread", -5, 5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("cake1" not in products.result, "error: cake1 was added with negative quantity and found")
        self.assertTrue("cake2" not in products.result, "error: cake2 was added with negative price and found")

        self.set_stock_permissions(False)
        r = self.app.add_product(self.session_id, "bakery3", "pita2", "bread", 10, 15, ["bread", "b1"])
        self.assertFalse(r.success or r.result, "error: add product action succeeded!")
        r = self.app.add_product(self.session_id, "bakery3", "borekas2", "bread", 5, 30, ["bread", "b2"])
        self.assertFalse(r.success or r.result, "error: add product action succeeded!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("pita2" not in products.result and "borekas2" not in products.result,
                        "error: pita2 and borekas2 found after added by a manager with no permissions")

        self.app.logout(self.session_id)
        self.app.register(self.session_id, "hacker3", "<$:_:$>")
        self.app.login(self.session_id, "hacker3", "<$:_:$>")
        r = self.app.add_product(self.session_id, "bakery3", "TNT", "special bread", 10, 15, ["specials", "bomb"])
        self.assertFalse(r.success, "error: add product action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("TNT" not in products.result, "error: TNT was added by someone without permission and found")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        self.exit_market()
        r = self.app.add_product(self.session_id, "bakery3", "cake3", "bread", 5, 5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("cake3" not in products.result, "error: cake3 added after exiting the market and found")
        self.exit_market()

    # todo - add change product quantity, keywords and category actions
    # Use Case: Update store inventory
    def test_change_product(self):
        # happy
        self.enter_market()
        self.set_stock_permissions(True)
        r = self.app.change_product_name(self.session_id, "bakery3", "pita", "new_pita")
        self.assertTrue(r.success and r.result, "error: change product name action failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("new_pita" in products.result, "error: pita product changed name to new_pita "
                                                       "and new_pita not found!")
        self.assertTrue("pita" not in products.result, "error: pita product changed name to new_pita "
                                                       "and pita found!")

        r = self.app.change_product_price(self.session_id, "bakery3", "new_pita", 30)
        self.assertTrue(r.success and r.result, "error: change product price action failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertEquals(products.result["new_pita"]["price"], 30, "error: manager changed new_pita price "
                                                                    "and the price didn't change")
        self.app.logout(self.session_id)

        # sad
        self.app.register(self.session_id, "not_owner", "pass1")
        self.app.login(self.session_id, "not_owner", "pass1")
        r = self.app.change_product_name(self.session_id, "bakery3", "borekas", "new_borekas")
        self.assertFalse(r.success, "error: change product name action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertTrue("new_borekas" not in products.result, "error: borekas product changed name to new_borekas "
                                                              "by a user with no permission")
        self.assertTrue("borekas" in products.result, "error: borekas product changed name to new_borekas "
                                                      "by a user with no permission and borekas not found")

        r = self.app.change_product_price(self.session_id, "bakery3", "borekas", 30)
        self.assertFalse(r.success, "error: change product price action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: borekas product changed price "
                                                                  "by a user with no permission and the price changed")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager5", "pass1")
        r = self.app.change_product_price(self.session_id, "bakery3", "borekas", -5)
        self.assertFalse(r.success, "error: change product price action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: price changed after a change price action "
                                                                  "with negative value")
        self.assertNotEquals(products.result["borekas"]["price"], -5, "error: product price changed to negative")

        self.set_stock_permissions(False)
        r = self.app.change_product_name(self.session_id, "bakery3", "new_pita", "old_pita")
        self.assertFalse(r.success or r.result, "error: change product name action succeeded!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertNotIn("old_pita", products.result, "error: new_pita product changed name to old_pita "
                                                      "by a manager with no permissions and new_pita not found!")
        self.assertIn("new_pita", products.result, "error: new_pita product changed name to old_pita "
                                                   "by a manager with no permissions and new_pita not found!")

        r = self.app.change_product_price(self.session_id, "bakery3", "new_pita", 20)
        self.assertFalse(r.success or r.result, "error: change product price action succeeded!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertEquals(products.result["new_pita"]["price"], 30, "error: manager with no permissions changed "
                                                                    "new_pita price and the price changed")
        self.app.logout(self.session_id)

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        r = self.app.change_product_price(self.session_id, "bakery3", "borekas", 10)
        self.assertFalse(r.success, "error: change product price action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: manager logged out and changed "
                                                                  "borekas price and the price changed")

        self.exit_market()
        r = self.app.change_product_name(self.session_id, "bakery3", "borekas", "new_borekas")
        self.assertFalse(r.success, "error: change product name action not failed!")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertNotIn("new_borekas", products.result, "error: borekas product changed name "
                                                         "after exiting the market")
        self.assertIn("borekas", products.result, "error: borekas product changed name after exiting the market")
        self.exit_market()

    # Use Case: Update store inventory
    def test_remove_product_from_store(self):
        # happy
        self.enter_market()
        self.set_stock_permissions(True)
        r = self.app.remove_product(self.session_id, "bakery3", "new_pita")
        self.assertTrue(r.success, "error: remove product action failed!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertNotIn("new_pita", products.result, "error: new_pita found in store after it was removed")

        # sad
        r = self.app.remove_product(self.session_id, "bakery3", "borekas123")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertIn("borekas", products.result, "error: borekas not found after a remove product action "
                                                  "on product borekas123")
        r = self.app.remove_product(self.session_id, "bakery123", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertIn("borekas", products.result, "error: borekas not found after a remove product action "
                                                  "on store bakery123")

        self.set_stock_permissions(False)
        r = self.app.remove_product(self.session_id, "bakery3", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded!")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertIn("borekas", products.result, "error: borekas not found in store after it was removed"
                                                  "by a manager with no permissions")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        r = self.app.remove_product(self.session_id, "bakery3", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertIn("borekas", products.result, "error: borekas not in bakery after "
                                                  "a remove product action after logged out")
        self.exit_market()
        r = self.app.remove_product(self.session_id, "bakery3", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery3")
        self.assertIn("borekas", products.result, "error: borekas not in bakery after "
                                                  "a remove product action after exiting the market")
        self.exit_market()

    # Use case: Get purchase history
    def test_purchase_history(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "manager5", "pass1")
        self.app.add_product(self.session_id, "bakery3", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery3", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer3", "123")
        self.app.login(self.session_id, "buyer3", "123")
        self.app.add_to_cart(self.session_id, "bakery3", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery3", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager5", "pass1")
        self.app.remove_product(self.session_id, "bakery3", "product1_1")
        self.app.change_product_price(self.session_id, "bakery3", "product1_2", 20)
        self.app.change_product_name(self.session_id, "bakery3", "product1_2", "new_name")
        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertTrue(r.success, "error: get store purchase history action failed")
        self.assertIn("product1_1", r.result, "error: product1_1 removed and no longer in purchase history "
                                              "although bought")
        self.assertIn("product1_2", r.result, "error: product1_2 changed name and price "
                                              "and no longer in purchase history")
        self.assertNotIn("new_name", r.result, "error: product1_2 changed name to new_name after a purchase"
                                               "and new_name shown in purchase history")
        self.assertTrue(r.result["product1_2"]["price"] == 16, "error: product1_2 changed price to 20 after a purchase"
                                                               "and the old price doesn't show in purchase history")

        # sad
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "new_user", "123")
        self.app.login(self.session_id, "new_user", "123")
        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: a user with no permissions got store purchase history")
        self.app.logout(self.session_id)

        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: a guest got store purchase history")

        self.set_stock_permissions(False)
        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: a manager with no permissions got store purchase history")

        # bad
        self.set_stock_permissions(True)
        self.app.logout(self.session_id)
        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error:manager got store purchase history after logout")
        self.app.logout(self.session_id)
        self.exit_market()
        r = self.app.get_store_purchase_history(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: manager got store purchase history after exiting the market")
        
    def test_get_store_personal(self):
        # allowed when has a personal permissions
        # happy
        self.enter_market()
        self.set_personal_permission(True)
        r = self.app.get_store_personal(self.session_id, "bakery3")
        self.assertTrue(r.success, "error: get store personal action failed!")
        self.assertIn("owner5", r.result, "error: owner5 not in personal list")
        self.assertIn("founder3", r.result, "error: founder3 not in personal list")
        self.assertIn("manager5", r.result, "error: manager5 not in personal list")

        # sad
        self.set_personal_permission(False)
        r = self.app.get_store_personal(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store personal action succeeded!")
        self.assertNotIn("owner5", r.result, "error: owner5 in personal list")
        self.assertNotIn("founder3", r.result, "error: founder3 in personal list")
        self.assertNotIn("manager5", r.result, "error: manager5 in personal list")

        # bad
        self.set_personal_permission(True)
        self.app.logout(self.session_id)
        r = self.app.get_store_personal(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store personal action succeeded")
        self.assertNotIn("owner5", r.result, "error: requested store personal after logout and owner5 in found")
        self.assertNotIn("founder3", r.result, "error: requested store personal after logout and founder3 in found")
        self.assertNotIn("manager5", r.result, "error: requested store personal after logout and manager5 in found")
        self.app.exit_market(self.session_id)
        r = self.app.get_store_personal(self.session_id, "bakery3")
        self.assertFalse(r.success, "error: get store personal action succeeded")
        self.assertNotIn("owner5", r.result, "error: requested store personal "
                                             "after exit the market and owner5 in found")
        self.assertNotIn("founder3", r.result, "error: requested store personal "
                                               "after exit the market and founder3 in found")
        self.assertNotIn("manager5", r.result, "error: requested store personal "
                                               "after exit the market and manager5 in found")