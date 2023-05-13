from domain.main.bridge.proxy import proxy
import unittest


class TestStoreOwner(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()
        self.enter_market()
        self.app.register(self.session_id, "founder1", "pass1")
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.open_store(self.session_id, "bakery")
        self.app.logout(self.session_id)
        self.exit_market()

    def enter_market(self):
        self.session_id = self.app.enter_market().result

    def exit_market(self):
        self.app.exit_market(self.session_id)

    # Use Case: Update store inventory
    def test_add_products_to_store(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.add_product(self.session_id, "bakery", "pita", "bread", 10, 15, ["bread", "b1"])
        self.assertTrue(r.success and r.result, "error: add product action failed!")
        r = self.app.add_product(self.session_id, "bakery", "borekas", "bread", 5, 30, ["bread", "b2"])
        self.assertTrue(r.success and r.result, "error: add product action failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("pita" and "borekas" in products.result, "pita and borekas not found")

        # sad
        r = self.app.add_product(self.session_id, "bakery", "cake1", "bread", 5, -5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        r = self.app.add_product(self.session_id, "bakery", "cake2", "bread", -5, 5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("cake1" not in products.result, "error: cake1 was added with negative quantity and found")
        self.assertTrue("cake2" not in products.result, "error: cake2 was added with negative price and found")

        self.app.logout(self.session_id)
        self.app.register(self.session_id, "hacker", "<$:_:$>")
        self.app.login(self.session_id, "hacker", "<$:_:$>")
        r = self.app.add_product(self.session_id, "bakery", "TNT", "special bread", 10, 15, ["specials", "bomb"])
        self.assertFalse(r.success, "error: add product action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("TNT" not in products.result, "error: TNT was added by someone without permission and found")

        # bad
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.logout(self.session_id)
        self.exit_market()
        r = self.app.add_product(self.session_id, "bakery", "cake3", "bread", 5, 5, ["bread", "b3"])
        self.assertFalse(r.success, "error: add product action not failed!")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("cake3" not in products.result, "error: cake3 added after exiting the market and found")
        self.exit_market()

    # todo - add change product quantity, keywords and category actions
    # Use Case: Update store inventory
    def test_change_product(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.change_product_name(self.session_id, "bakery", "pita", "new_pita")
        self.assertTrue(r.success and r.result, "error: change product name action failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("new_pita" in products.result, "error: pita product changed name to new_pita "
                                                       "and new_pita not found!")
        self.assertTrue("pita" not in products.result, "error: pita product changed name to new_pita "
                                                       "and pita found!")

        r = self.app.change_product_price(self.session_id, "bakery", "new_pita", 30)
        self.assertTrue(r.success and r.result, "error: change product price action failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertEquals(products.result["new_pita"]["price"], 20, "error: owner changed new_pita price "
                                                                    "and the price didn't change")
        self.app.logout(self.session_id)

        # sad
        self.app.register(self.session_id, "not_owner", "pass1")
        self.app.login(self.session_id, "not_owner", "pass1")
        r = self.app.change_product_name(self.session_id, "bakery", "borekas", "new_borekas")
        self.assertFalse(r.success, "error: change product name action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("new_borekas" not in products.result, "error: borekas product changed name to new_borekas "
                                                              "by a user with no permission")
        self.assertTrue("borekas" in products.result, "error: borekas product changed name to new_borekas "
                                                      "by a user with no permission and borekas not found")

        r = self.app.change_product_price(self.session_id, "bakery", "borekas", 30)
        self.assertFalse(r.success, "error: change product price action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: borekas product changed price "
                                                                  "by a user with no permission and the price changed")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.change_product_price(self.session_id, "bakery", "borekas", -5)
        self.assertFalse(r.success, "error: change product price action not failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: price changed after a change price action "
                                                                  "with negative value")
        self.assertNotEquals(products.result["borekas"]["price"], -5, "error: product price changed to negative")

        # bad
        self.app.logout(self.session_id)
        self.app.exit_market(self.session_id)
        r = self.app.change_product_price(self.session_id, "bakery", "borekas", 10)
        self.assertFalse(r.success, "error: change product price action not failed!")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertEquals(products.result["borekas"]["price"], 5, "error: price changed after exiting the market")
        self.assertNotEquals(products.result["borekas"]["price"], 10, "error: price changed after exiting the market")

        self.app.exit_market(self.session_id)
        r = self.app.change_product_name(self.session_id, "bakery", "borekas", "new_borekas")
        self.assertFalse(r.success, "error: change product name action not failed!")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue("new_borekas" not in products.result, "error: borekas product changed name "
                                                              "after exiting the market")
        self.assertTrue("borekas" in products.result, "error: borekas product changed name after exiting the market")
        self.exit_market()

    # Use Case: Update store inventory
    def test_remove_product_from_store(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.remove_product(self.session_id, "bakery", "new_pita")
        self.assertTrue(r.success, "error: remove product action failed!")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertNotIn("new_pita", products.result, "error: new_pita found in store after it was removed")

        # sad
        r = self.app.remove_product(self.session_id, "bakery", "borekas123")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertIn("borekas", products.result, "error: borekas not found after a remove product action "
                                                  "on product borekas123")
        r = self.app.remove_product(self.session_id, "bakery123", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertIn("borekas", products.result, "error: borekas not found after a remove product action "
                                                  "on store bakery123")

        # bad
        self.app.logout(self.session_id)
        r = self.app.remove_product(self.session_id, "bakery", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertIn("borekas", products.result, "error: borekas not in bakery after "
                                                  "a remove product action while logged out")
        self.app.exit_market(self.session_id)
        r = self.app.remove_product(self.session_id, "bakery", "borekas")
        self.assertFalse(r.success, "error: remove product action succeeded")
        self.enter_market()
        products = self.app.get_store_products(self.session_id, "bakery")
        self.assertIn("borekas", products.result, "error: borekas not in bakery after "
                                                  "a remove product action after exiting the market")
        self.exit_market()

    # Use Case: Appoint store manager 
    def test_add_manager(self):
        # happy
        self.enter_market()
        self.app.register(self.session_id, "manager1", "pass1")
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.appoint_manager(self.session_id, "bakery", "manager1")
        self.assertTrue(r.success, "error: appoint manager action failed")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertIn("founder1", personal.result, "error: founder1 not in personal list of its shop")
        self.assertIn("manager1", personal.result, "error: manager1 not in personal list after appointed")

        # sad
        r = self.app.appoint_manager(self.session_id, "bakery", "not_registered_user")
        self.assertFalse(r.success, "error: add manager action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("not_registered_user", personal.result, "error: not_registered_user in personal list "
                                                                 "after add manager action")

        self.app.logout(self.session_id)
        self.app.register(self.session_id, "manager2", "pass1")
        self.app.register(self.session_id, "manager3", "pass1")
        self.app.login(self.session_id, "manager2", "pass1")
        r = self.app.appoint_manager(self.session_id, "bakery", "manager3")
        self.assertFalse(r.success, "error: add manager action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("manager3", personal.result, "error: manager3 in personal list after add manager action "
                                                      "of a user without permissions")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "manager3", "pass1")
        r = self.app.appoint_manager(self.session_id, "bakery", "manager3")
        self.assertFalse(r.success, "error: add manager action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("manager3", personal.result, "error: manager3 in personal list after add manager action "
                                                      "made by him, manager3 don't have permissions")

        # bad
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.logout(self.session_id)
        r = self.app.appoint_manager(self.session_id, "bakery", "manager3")
        self.assertFalse(r.success, "error: add manager action succeeded!")
        self.app.login(self.session_id, "founder1", "pass1")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("manager3", personal.result, "error: manager3 in personal list, "
                                                      "he appointed after founder1 was logged out")

        self.app.logout(self.session_id)
        self.exit_market()
        r = self.app.appoint_manager(self.session_id, "bakery", "manager3")
        self.assertFalse(r.success, "error: add manager action succeeded!")
        self.exit_market()
        self.app.login(self.session_id, "founder1", "pass1")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("manager3", personal.result, "error: manager3 in personal list, "
                                                      "he appointed after founder1 was exited the market")

    # Use Case: Appoint store owner 
    def test_add_owner(self):
        # happy
        self.enter_market()
        self.app.register(self.session_id, "owner1", "pass1")
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.appoint_owner(self.session_id, "bakery", "owner1")
        self.assertTrue(r.success, "error: appoint owner action failed")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertIn("founder1", personal.result, "error: founder1 not in personal list of its shop")
        self.assertIn("owner1", personal.result, "error: owner1 not in personal list after appointed")

        # sad
        r = self.app.appoint_owner(self.session_id, "bakery", "not_registered_user")
        self.assertFalse(r.success, "error: add owner action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("not_registered_user", personal.result, "error: not_registered_user in personal list "
                                                                 "after add owner action")

        self.app.logout(self.session_id)
        self.app.register(self.session_id, "owner2", "pass1")
        self.app.register(self.session_id, "owner3", "pass1")
        self.app.login(self.session_id, "owner2", "pass1")
        r = self.app.appoint_owner(self.session_id, "bakery", "owner3")
        self.assertFalse(r.success, "error: add owner action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("owner3", personal.result, "error: owner3 in personal list after add owner action "
                                                    "of a user without permissions")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "owner3", "pass1")
        r = self.app.appoint_owner(self.session_id, "bakery", "owner3")
        self.assertFalse(r.success, "error: add owner action succeeded!")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("owner3", personal.result, "error: owner3 in personal list after add manager action "
                                                    "made by him, owner3 don't have permissions")

        # bad
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.logout(self.session_id)
        r = self.app.appoint_owner(self.session_id, "bakery", "owner3")
        self.assertFalse(r.success, "error: add owner action succeeded!")
        self.app.login(self.session_id, "founder1", "pass1")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("owner3", personal.result, "error: owner3 in personal list, "
                                                    "he appointed after founder1 was logged out")

        self.app.logout(self.session_id)
        self.exit_market()
        r = self.app.appoint_owner(self.session_id, "bakery", "owner3")
        self.assertFalse(r.success, "error: add owner action succeeded!")
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        personal = self.app.get_store_personal(self.session_id, "bakery")
        self.assertNotIn("owner3", personal.result, "error: owner3 in personal list, "
                                                    "he appointed after founder1 was exited the market")
        self.exit_market()

    # Use Case: Close a store
    def test_close_store(self):
        # happy
        self.enter_market()
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery", "borekas", 3)
        self.app.buy_cart_with_card(self.session_id, "1234123412341234", "123", "01/01/2025")

        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.personal_before_closing = self.app.get_store_personal(self.session_id, "bakery")
        r = self.app.close_store(self.session_id, "bakery")
        self.assertTrue(r.success, "error: close store action failed")
        personal_after_closing = self.app.get_store_personal(self.session_id, "bakery")
        self.assertEquals(self.personal_before_closing, personal_after_closing, "error: store personal info changed "
                                                                                "after closing the store!")

        purchase_history = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertTrue(purchase_history.success, "error: get store purchase history action failed")
        self.assertTrue(len(purchase_history.result) != 0, "error: purchase history is empty after closing the store")
        self.app.logout(self.session_id)

        r = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue(r.success, "error: get store products action failed")
        self.assertTrue(len(r.result) == 0, "error: store closed but its products found in a store products search")
        r = self.app.get_products_by_name(self.session_id, "borekas")
        self.assertTrue(r.success, "error: get products by name action failed")
        self.assertNotIn("bakery", r.result, "error: store closed but is found in a product name search")
        self.assertNotIn("borekas", r.result, "error: store closed but its products found in a product name search")

        # sad
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.close_store(self.session_id, "notReal")
        self.assertFalse(r.success, "error: founder of bakery closed a not existing store")
        self.app.logout(self.session_id)

        self.app.login(self.session_id, "owner1", "pass1")
        r = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a owner - not the founder closed the store")
        self.app.logout(self.session_id)

        self.app.login(self.session_id, "manager1", "pass1")
        r = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a manager - not the founder closed the store")
        self.app.logout(self.session_id)

        self.app.register(self.session_id, "random1", "pass1")
        self.app.login(self.session_id, "random1", "pass1")
        r = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a user - not the founder closed the store")
        self.app.logout(self.session_id)

        # bad
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.logout(self.session_id)
        r = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: founder closed the store after logout")

        self.exit_market()
        r = self.app.close_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: founder closed the store after exiting the market")

    # Use Case: Open a store
    def test_open_store(self):
        # happy - bakery store is closed because of last test
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        personal_before_opening = self.app.get_store_personal(self.session_id, "bakery")
        r = self.app.open_store(self.session_id, "bakery")
        self.assertTrue(r.success, "error: open store action failed")
        personal_after_opening = self.app.get_store_personal(self.session_id, "bakery")
        self.assertEquals(personal_before_opening, personal_after_opening, "error: store personal info changed "
                                                                           "after opening the store!")
        self.assertEquals(self.personal_before_closing, personal_after_opening, "error: store personal info changed "
                                                                                "after closing and opening the store!")

        purchase_history = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertTrue(purchase_history.success, "error: get store purchase history action failed")
        self.assertTrue(len(purchase_history.result) != 0, "error: purchase history is empty after opening the store")
        self.app.logout(self.session_id)

        r = self.app.get_store_products(self.session_id, "bakery")
        self.assertTrue(r.success, "error: get store products action failed")
        self.assertTrue(len(r.result) != 0, "error: store opened but its products not found in a store products search")
        r = self.app.get_products_by_name(self.session_id, "borekas")
        self.assertTrue(r.success, "error: get products by name action failed")
        self.assertIn("bakery", r.result, "error: store opened but is not found in a product name search")
        self.assertIn("borekas", r.result, "error: store opened but its products not found in a product name search")

        # sad
        self.app.login(self.session_id, "founder1", "pass1")
        r = self.app.close_store(self.session_id, "bakery")
        self.app.logout(self.session_id)

        self.app.login(self.session_id, "owner1", "pass1")
        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a owner - not the founder reopened the store")
        self.app.logout(self.session_id)

        self.app.login(self.session_id, "manager1", "pass1")
        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a manager - not the founder reopened the store")
        self.app.logout(self.session_id)

        self.app.register(self.session_id, "random1", "pass1")
        self.app.login(self.session_id, "random1", "pass1")
        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a user - not the founder reopened the store")
        self.app.logout(self.session_id)

        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: a guest - not the founder reopened the store")

        r = self.app.open_store(self.session_id, "new store")
        self.assertFalse(r.success, "error: a guest - opened a store")

        # bad
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.logout(self.session_id)
        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: founder reopened the store after logout")

        self.exit_market()
        r = self.app.open_store(self.session_id, "bakery")
        self.assertFalse(r.success, "error: founder reopened the store after exiting the market")

    # Use case: Get purchase history
    def test_purchase_history(self):
        # happy
        self.enter_market()
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.add_product(self.session_id, "bakery", "product1_1", "cat1", 12, 15, ["car1", "p1"])
        self.app.add_product(self.session_id, "bakery", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
        self.app.logout(self.session_id)
        self.app.register(self.session_id, "buyer1", "123")
        self.app.login(self.session_id, "buyer1", "123")
        self.app.add_to_cart(self.session_id, "bakery", "product1_1", 5)
        self.app.add_to_cart(self.session_id, "bakery", "product1_2", 10)
        self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345")
        self.app.logout(self.session_id)
        self.app.login(self.session_id, "founder1", "pass1")
        self.app.remove_product(self.session_id, "bakery", "product1_1")
        self.app.change_product_price(self.session_id, "bakery", "product1_2", 20)
        self.app.change_product_name(self.session_id, "bakery", "product1_2", "new_name")
        r = self.app.get_store_purchase_history(self.session_id, "bakery")
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
        r = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: a user with no permissions got store purchase history")
        self.app.logout(self.session_id)

        r = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: a gues got store purchase history")

        # bad
        self.exit_market()
        r = self.app.get_store_purchase_history(self.session_id, "bakery")
        self.assertFalse(r.success, "error: get store purchase history action succeeded")
        self.assertNotIn("product1_1", r.result, "error: got store purchase history after exiting the market")

