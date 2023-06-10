    #
    # # Use Case: Appoint store manager
    # def test_add_manager(self):
    #     # happy
    #     self.enter_market()
    #     self.app.register(self.session_id, "manager01", "pass1")
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     r = self.app.appoint_manager(self.session_id, "bakery2", "manager01")
    #     self.assertTrue(r.success, "error: appoint manager action failed")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertIn("owner01", personal.result, "error: founder2 not in personal list of its shop")
    #     self.assertIn("manager01", personal.result, "error: manager1 not in personal list after appointed")
    #
    #     # sad
    #     r = self.app.appoint_manager(self.session_id, "bakery2", "not_registered_user")
    #     self.assertFalse(r.success, "error: add manager action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("not_registered_user", personal.result, "error: not_registered_user in personal list "
    #                                                              "after add manager action")
    #
    #     self.app.logout(self.session_id)
    #     self.app.register(self.session_id, "manager02", "pass1")
    #     self.app.register(self.session_id, "manager03", "pass1")
    #     self.app.login(self.session_id, "manager02", "pass1")
    #     r = self.app.appoint_manager(self.session_id, "bakery2", "manager03")
    #     self.assertFalse(r.success, "error: add manager action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("manager03", personal.result, "error: manager03 in personal list after add manager action "
    #                                                    "of a user without permissions")
    #
    #     self.app.logout(self.session_id)
    #     self.app.login(self.session_id, "manager03", "pass1")
    #     r = self.app.appoint_manager(self.session_id, "bakery2", "manager03")
    #     self.assertFalse(r.success, "error: add manager action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("manager03", personal.result, "error: manager03 in personal list after add manager action "
    #                                                    "made by him, manager03 don't have permissions")
    #
    # # Use Case: Appoint store owner
    # def test_add_owner(self):
    #     # happy
    #     self.enter_market()
    #     self.app.register(self.session_id, "owner02", "pass1")
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "owner02")
    #     self.assertTrue(r.success, "error: appoint owner action failed")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertIn("owner01", personal.result, "error: owner01 not in personal list of its shop")
    #     self.assertIn("owner02", personal.result, "error: owner02 not in personal list after appointed")
    #
    #     # sad
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "not_registered_user")
    #     self.assertFalse(r.success, "error: add owner action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("not_registered_user", personal.result, "error: not_registered_user in personal list "
    #                                                              "after add owner action")
    #
    #     self.app.logout(self.session_id)
    #     self.app.register(self.session_id, "owner02", "pass1")
    #     self.app.register(self.session_id, "owner03", "pass1")
    #     self.app.login(self.session_id, "owner02", "pass1")
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "owner03")
    #     self.assertFalse(r.success, "error: add owner action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("owner03", personal.result, "error: owner03 in personal list after add owner action "
    #                                                  "of a user without permissions")
    #
    #     self.app.logout(self.session_id)
    #     self.app.login(self.session_id, "owner03", "pass1")
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "owner03")
    #     self.assertFalse(r.success, "error: add owner action succeeded!")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("owner03", personal.result, "error: owner03 in personal list after add manager action "
    #                                                  "made by him, owner03 don't have permissions")
    #
    #     # bad
    #     self.app.logout(self.session_id)
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     self.app.logout(self.session_id)
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "owner03")
    #     self.assertFalse(r.success, "error: add owner action succeeded!")
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("owner03", personal.result, "error: owner03 in personal list, "
    #                                                  "he appointed after founder2 was logged out")
    #
    #     self.app.logout(self.session_id)
    #     self.exit_market()
    #     r = self.app.appoint_owner(self.session_id, "bakery2", "owner3")
    #     self.assertFalse(r.success, "error: add owner action succeeded!")
    #     self.enter_market()
    #     self.app.login(self.session_id, "founder2", "pass1")
    #     personal = self.app.get_store_personal(self.session_id, "bakery2")
    #     self.assertNotIn("owner03", personal.result, "error: owner03 in personal list, "
    #                                                  "he appointed after founder2 was exited the market")
    #     self.exit_market()
    #
    # # Use case: Get purchase history
    # def test_purchase_history(self):
    #     # happy
    #     self.enter_market()
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     self.app.add_product(self.session_id, "bakery2", "product1_1", "cat1", 12, 15, ["car1", "p1"])
    #     self.app.add_product(self.session_id, "bakery2", "product1_2", "cat2", 16, 9, ["cat2", "p2"])
    #     self.app.logout(self.session_id)
    #     self.app.register(self.session_id, "buyer2", "123")
    #     self.app.login(self.session_id, "buyer2", "123")
    #     self.app.add_to_cart(self.session_id, "bakery2", "product1_1", 5)
    #     self.app.add_to_cart(self.session_id, "bakery2", "product1_2", 10)
    #     self.app.buy_cart_with_paypal(self.session_id, "user1234", "12345", "zambabir", "010101")
    #     self.app.logout(self.session_id)
    #     self.app.login(self.session_id, "owner01", "pass1")
    #     self.app.remove_product(self.session_id, "bakery2", "product1_1")
    #     self.app.change_product_price(self.session_id, "bakery2", "product1_2", 20)
    #     self.app.change_product_name(self.session_id, "bakery2", "product1_2", "new_name")
    #     r = self.app.get_store_purchase_history(self.session_id, "bakery2")
    #     self.assertTrue(r.success, "error: get store purchase history action failed")
    #     self.assertIn("product1_1", r.result, "error: product1_1 removed and no longer in purchase history "
    #                                           "although bought")
    #     self.assertIn("product1_2", r.result, "error: product1_2 changed name and price "
    #                                           "and no longer in purchase history")
    #     self.assertNotIn("new_name", r.result, "error: product1_2 changed name to new_name after a purchase"
    #                                            "and new_name shown in purchase history")
    #     self.assertTrue(r.result["product1_2"]["price"] == 16, "error: product1_2 changed price to 20 after a purchase"
    #                                                            "and the old price doesn't show in purchase history")
    #
    #     # sad
    #     self.app.logout(self.session_id)
    #     self.app.register(self.session_id, "new_user2", "123")
    #     self.app.login(self.session_id, "new_user2", "123")
    #     r = self.app.get_store_purchase_history(self.session_id, "bakery2")
    #     self.assertFalse(r.success, "error: get store purchase history action succeeded")
    #     self.assertNotIn("product1_1", r.result, "error: a user with no permissions got store purchase history")
    #     self.app.logout(self.session_id)
    #
    #     r = self.app.get_store_purchase_history(self.session_id, "bakery2")
    #     self.assertFalse(r.success, "error: get store purchase history action succeeded")
    #     self.assertNotIn("product1_1", r.result, "error: a gues got store purchase history")
    #
    #     # bad
    #     self.exit_market()
    #     r = self.app.get_store_purchase_history(self.session_id, "bakery2")
    #     self.assertFalse(r.success, "error: get store purchase history action succeeded")
    #     self.assertNotIn("product1_1", r.result, "error: got store purchase history after exiting the market")
    #
    #
    #
