from unittest.mock import patch
from Service.bridge.proxy import Proxy
import unittest
from domain.main.Market import Permissions
from domain.main.Market.Permissions import Permission


class AppointManager(unittest.TestCase):
    app: Proxy = Proxy()
    manager_default_permissions = None
    not_manager_default_permissions = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_owner2 = ("usr6", "password")
        cls.store_manager1 = ("usr4", "password")
        cls.store_manager2 = ("usr7", "password")
        cls.registered_user = ("user5", "password")
        cls.manager_default_permissions = Permissions.get_default_manager_permissions()
        cls.not_manager_default_permissions = set()
        for p in Permission:
            if p not in cls.manager_default_permissions:
                cls.not_manager_default_permissions.add(p)

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.store_manager1)
        self.app.register(*self.store_manager2)
        self.app.register(*self.registered_user)
        self.set_stores()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_appoint_manager_by_founder(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_manager1[0]]["Appointed by"],
                         "error: Appointed By value is incorrect")
        for p in self.manager_default_permissions:
            self.assertIn(p.value, appointment[self.store_manager1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in self.not_manager_default_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager1[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    def test_appoint_manager_by_owner(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_owner(self.store_owner2[0], "bakery")
        self.assertTrue(r.success, "error: appoint owner action failed")
        self.app.logout()
        self.app.login(*self.store_owner2)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_owner2[0], appointment[self.store_manager1[0]]["Appointed by"],
                         "error: Appointed By value is incorrect")
        for p in self.manager_default_permissions:
            self.assertIn(p.value, appointment[self.store_manager1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in self.not_manager_default_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager1[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    def test_appoint_manager_by_owner_without_permissions(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_owner(self.store_owner2[0], "bakery")
        self.assertTrue(r.success, "error: appoint owner action failed")
        r = self.app.remove_permission("bakery", self.store_owner2[0], Permission.AppointManager)
        self.assertTrue(r.success, "error: remove permission action failed")
        self.app.logout()
        self.app.login(*self.store_owner2)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_appoint_manager_by_manager_with_permissions(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_manager(self.store_manager2[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        r = self.app.add_permission("bakery", self.store_manager2[0], Permission.AppointManager)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager2)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_manager2[0], appointment[self.store_manager1[0]]["Appointed by"],
                         "error: appointed by value is incorrect")
        for p in self.manager_default_permissions:
            self.assertIn(p.value, appointment[self.store_manager1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in self.not_manager_default_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager1[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    def test_appoint_manager_by_manager_without_permissions(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_manager(self.store_manager2[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_appoint_manager_by_a_member(self):
        self.app.login(*self.registered_user)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_guest_with_no_permission_to_appoint(self):
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_appointing_founder_to_be_manager(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_owner(self.store_owner2[0], "bakery")
        self.assertTrue(r.success, "error: appoint owner action failed")
        self.app.logout()
        self.app.login(*self.store_owner2)
        r = self.app.appoint_manager(self.store_founder1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_founder1[0], appointment)
        self.assertEqual(None, appointment[self.store_founder1[0]]["Appointed by"])
        for p in Permission:
            self.assertIn(p.value, appointment[self.store_founder1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "owner")

    def test_circular_appointments(self):
        self.app.login(*self.store_founder1)
        r = self.app.appoint_manager(self.store_manager2[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.AppointManager)
        self.assertTrue(r.success, "error: add permission action failed")
        r = self.app.add_permission("bakery", self.store_manager2[0], Permission.AppointManager)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager2)
        r = self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_manager(self.registered_user[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.registered_user[0], appointment)
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_manager1[0]]["Appointed by"])
        new_permissions = self.manager_default_permissions.copy()
        new_permissions.add(Permission.AppointManager)
        not_new_permissions = self.not_manager_default_permissions.copy()
        not_new_permissions.discard(Permission.AppointManager)
        for p in new_permissions:
            self.assertIn(p.value, appointment[self.store_manager1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in not_new_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager1[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    # permissions tests #
    def test_retrieve_purchase_history(self):
        with patch(self.app.provision_path, return_value=True), \
                patch(self.app.payment_pay_path, return_value=True):

            self.set_appointments()
            self.app.login(*self.store_founder1)
            r = self.app.add_permission("bakery", self.store_manager1[0], Permission.RetrievePurchaseHistory)
            self.assertTrue(r.success, "error: add permission action failed")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 10)
            self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
            self.app.login(*self.store_manager1)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("bread", purchase_history, "error: a manager with permission can't see the purchase history")

    def test_retrieve_staff_details(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.RetrieveStaffDetails)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get staff details action failed")
        appointment = r.result
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_manager1[0]]["Appointed by"])
        self.assertIn(self.store_owner2[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_owner2[0]]["Appointed by"])
        new_permissions = self.manager_default_permissions.copy()
        new_permissions.add(Permission.RetrieveStaffDetails)
        not_new_permissions = self.not_manager_default_permissions.copy()
        not_new_permissions.discard(Permission.RetrieveStaffDetails)
        for p in new_permissions:
            self.assertIn(p.value, appointment[self.store_manager1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in not_new_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager1[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    def test_add_a_product(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Add)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.add_product("bakery", "lafa", "1", 5, 20, ["basic", "x"])
        self.assertTrue(r.success, "error: add product action failed")
        store = self.app.get_store("bakery").result
        self.assertIn("lafa", store, "error: lafa not found")
        self.assertEqual("lafa", store["lafa"]["Name"], "error: lafa name incorrect")
        self.assertEqual(5, store["lafa"]["Price"], "error: lafa price incorrect")
        self.assertEqual("1", store["lafa"]["Category"], "error: lafa category incorrect")
        self.assertEqual(5, store["lafa"]["Rate"], "error: lafa rate incorrect")
        self.assertEqual(20, store["lafa"]["Quantity"], "error: lafa quantity incorrect")

    def test_update_product_quantity(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Update)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.update_product_quantity("bakery", "bread", 50)
        self.assertTrue(r.success, "error: update product quantity action failed")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(50, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_update_product_name(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Update)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_name("bakery", "bread", "new_bread")
        self.assertTrue(r.success, "error: update product quantity action failed")
        store = self.app.get_store("bakery").result
        self.assertIn("new_bread", store, "error: new_bread not found")
        self.assertEqual("new_bread", store["new_bread"]["Name"], "error: new_bread name incorrect")
        self.assertEqual(10, store["new_bread"]["Price"], "error: new_bread price incorrect")
        self.assertEqual("1", store["new_bread"]["Category"], "error: new_bread category incorrect")
        self.assertEqual(5, store["new_bread"]["Rate"], "error: new_bread rate incorrect")
        self.assertEqual(15, store["new_bread"]["Quantity"], "error: new_bread quantity incorrect")

    def test_update_product_price(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Update)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_price("bakery", 10, 30)
        self.assertTrue(r.success, "error: update product price action failed")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(30, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_update_product_category(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Update)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_category("bakery", "bread", "5")
        self.assertTrue(r.success, "error: update product price action failed")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("5", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_remove_product(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.Remove)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.remove_product("bakery", "bread")
        self.assertTrue(r.success, "error: remove product action failed")
        store = self.app.get_store("bakery").result
        self.assertNotIn("bread", store, "error: bread found after removed by owner with permissions")

    def test_appoint_another_manager(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.AppointManager)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_manager(self.store_manager2[0], "bakery")
        self.assertTrue(r.success, "error: appoint manager action failed")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_manager2[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_manager2[0]]["Appointed by"])
        for p in self.manager_default_permissions:
            self.assertIn(p.value, appointment[self.store_manager2[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                       "not found for an appointed "
                                                                                       "manager")
        for p in self.not_manager_default_permissions:
            self.assertNotIn(p.value, appointment[self.store_manager2[0]]["Permissions"],
                             f"error: permission '{p.value}' "
                             "found for an appointed manager")

    def test_appoint_another_owner(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.AppointOwner)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.assertTrue(r.success, "error: appoint owner action failed")
        self.app.logout()
        self.app.login(*self.store_founder1)
        self.app.approve_owner(self.store_owner1[0], "bakery")
        r = self.app.get_store_staff("bakery")
        self.assertTrue(r.success, "error: get store staff action failed")
        appointment = r.result
        self.assertIn(self.store_owner1[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_owner1[0]]["Appointed by"])
        for p in Permission:
            self.assertIn(p.value, appointment[self.store_owner1[0]]["Permissions"], f"error: permission '{p.value}' "
                                                                                     "not found for an appointed "
                                                                                     "manager")

    def test_interact_with_customer(self):
        pass

    def test_add_a_store_rule(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.AddRule)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r1 = self.app.add_simple_discount("bakery", "product", 50, "bread")
        self.assertTrue(r1.success, "error: add simple discount action failed")
        r2 = self.app.add_simple_discount("bakery", "product", 30, "bread")
        self.assertTrue(r2.success, "error: add simple discount action failed")
        r = self.app.connect_discounts("bakery", r1.result, r2.result, "max", "simple",
                                       p1_name="bread", gle1=">", amount1=3)
        self.assertTrue(r.success, "error: connect discount action failed")
        r = self.app.get_purchase_rules("bakery")
        self.assertTrue(r.success, "error: get discounts action failed")
        self.assertNotEqual({}, r.result, "error: owner don't see the purchase rules")

    def test_change_discount_policy(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.ChangeDiscountPolicy)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r1 = self.app.add_simple_discount("bakery", "product", 50, "bread")
        self.assertTrue(r1.success, "error: add simple discount action failed")
        r2 = self.app.add_simple_discount("bakery", "product", 30, "pita")
        self.assertTrue(r2.success, "error: add simple discount action failed")
        r3 = self.app.connect_discounts("bakery", r1.result, r2.result, "max", "simple",
                                        p1_name="bread", gle1=">", amount1=3)
        self.assertTrue(r3.success, "error: connect discount action failed")
        r = self.app.get_discounts("bakery")
        simples = r.result[0]
        connectors = r.result[1]
        self.assertTrue(r.success, "error: get discounts action failed")
        self.assertIn(r1.result, simples, "error: first discount not found")
        self.assertIn(r2.result, simples, "error: second discount not found")
        self.assertIn("simple discount: 50% for bread", simples[r1.result], "error: first discount doesn't match")
        self.assertIn("simple discount: 30% for pita", simples[r2.result], "error: second discount doesn't match")
        self.assertIn(r3.result, connectors, "error: connector discount not found")
        self.assertIn(f"Max connector: id: {r1.result}     id: {r2.result}", connectors[r3.result],
                      "error: connector discount doesn't match")
        self.assertIn(f"Add connector: id: {r3.result}", connectors["bakery"],
                      "error: second discount doesn't match")

    def test_start_a_bid(self):
        self.set_appointments()
        self.app.login(*self.store_founder1)
        r = self.app.add_permission("bakery", self.store_manager1[0], Permission.StartBid)
        self.assertTrue(r.success, "error: add permission action failed")
        self.app.logout()
        self.app.login(*self.store_manager1)
        r = self.app.start_bid("bakery", "bread")
        self.assertTrue(r.success, "error: start a bid action failed")
        self.app.logout()
        self.app.login(*self.registered_user)
        r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                        "ben-gurion", "1234", 10.5, "beer sheva", "israel")
        self.assertTrue(r.success, "error: purchase with a bid policy failed")
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        self.assertIn("bread", r.result, "error: no bid found for a bread after a owner started a bid")
        self.assertEqual(10.5, r.result["bread"])

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()

    def set_appointments(self):
        self.app.login(*self.store_founder1)
        self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.app.appoint_owner(self.store_owner2[0], "bakery")
        self.app.logout()
