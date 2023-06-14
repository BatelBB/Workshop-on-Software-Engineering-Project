from unittest.mock import patch
import unittest
from Service.bridge.proxy import Proxy
from domain.main.Market.Permissions import Permission


class RemoveOwner(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_owner2 = ("usr6", "password")
        cls.store_manager1 = ("usr4", "password")
        cls.store_manager2_2 = ("usr7", "password")
        cls.store_manager1_2 = ("usr10", "password")
        cls.store_owner1_2 = ("usr8", "password")
        cls.store_owner2_2 = ("usr9", "password")
        cls.registered_user = ("user5", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.store_manager1)
        self.app.register(*self.store_manager1_2)
        self.app.register(*self.store_manager2_2)
        self.app.register(*self.store_owner1_2)
        self.app.register(*self.store_owner2_2)
        self.app.register(*self.registered_user)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_cascading_remove_appointment(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.app.add_permission("bakery", self.store_manager1[0], Permission.AppointOwner)
        self.app.add_permission("bakery", self.store_manager1[0], Permission.AppointManager)
        self.app.logout()
        self.app.login(*self.store_owner1)
        self.app.appoint_owner(self.store_owner1_2[0], "bakery")
        self.app.appoint_manager(self.store_manager1_2[0], "bakery")
        self.app.add_permission("bakery", self.store_manager1_2[0], Permission.Add)
        self.app.logout()
        self.app.login(*self.store_manager1)
        self.app.appoint_owner(self.store_owner2_2[0], "bakery")
        self.app.appoint_manager(self.store_manager2_2[0], "bakery")
        self.app.add_permission("bakery", self.store_manager2_2[0], Permission.Add)
        self.app.logout()
        self.approve_owner(self.store_owner1_2, [self.store_founder1, self.store_owner1])
        self.approve_owner(self.store_owner2_2, [self.store_founder1, self.store_owner1, self.store_owner1_2])
        self.app.login(*self.store_founder1)
        appointment = self.app.get_store_staff("bakery").result
        self.assertIn(self.store_owner1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_owner1[0]]["Appointed by"])
        self.assertIn(self.store_owner1_2[0], appointment)
        self.assertEqual(self.store_owner1[0], appointment[self.store_owner1_2[0]]["Appointed by"])
        self.assertIn(self.store_manager1_2[0], appointment)
        self.assertEqual(self.store_owner1[0], appointment[self.store_manager1_2[0]]["Appointed by"])
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_manager1[0]]["Appointed by"])
        self.assertIn(self.store_owner2_2[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_owner2_2[0]]["Appointed by"])
        self.assertIn(self.store_manager2_2[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_manager2_2[0]]["Appointed by"])
        r = self.app.remove_appointment(self.store_owner1[0], "bakery")
        self.assertTrue(r.success, "error: remove appointment action failed")
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.store_owner1[0], appointment)
        self.assertNotIn(self.store_owner1_2[0], appointment)
        self.assertNotIn(self.store_manager1_2[0], appointment)
        self.assertIn(self.store_manager1[0], appointment)
        self.assertEqual(self.store_founder1[0], appointment[self.store_manager1[0]]["Appointed by"])
        self.assertIn(self.store_owner2_2[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_owner2_2[0]]["Appointed by"])
        self.assertIn(self.store_manager2_2[0], appointment)
        self.assertEqual(self.store_manager1[0], appointment[self.store_manager2_2[0]]["Appointed by"])
        self.app.remove_appointment(self.store_manager1[0], "bakery")
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.store_owner1[0], appointment)
        self.assertNotIn(self.store_owner1_2[0], appointment)
        self.assertNotIn(self.store_manager1_2[0], appointment)
        self.assertNotIn(self.store_manager1[0], appointment)
        self.assertNotIn(self.store_owner2_2[0], appointment)
        self.assertNotIn(self.store_manager2_2[0], appointment)
        self.app.logout()
        self.app.login(*self.store_owner1_2)
        r = self.app.add_product("bakery", "lafa", "1", 8, 10, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa not found")
        self.app.logout()
        self.app.login(*self.store_manager1_2)
        r = self.app.add_product("bakery", "lafa", "1", 8, 10, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa not found")
        self.app.logout()
        self.app.login(*self.store_owner2_2)
        r = self.app.add_product("bakery", "lafa", "1", 8, 10, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa not found")
        self.app.logout()
        self.app.login(*self.store_manager2_2)
        r = self.app.add_product("bakery", "lafa", "1", 8, 10, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa not found")

    def test_product_added_by_owner_is_in_store_after_owner_removed(self):
        self.set_store_and_appointments()
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")

    def test_fail_to_retrieve_purchase_history(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True), \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True):
            self.set_store_and_appointments()
            self.app.add_to_cart("bakery", "bread", 10)
            self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
            self.app.login(*self.store_owner1)
            r = self.app.get_store_purchase_history("bakery")
            self.assertFalse(r.success, "error: get purchase history action succeeded")
            self.assertEqual(None, r.result, "error: owner got purchase history after removed")

    def test_fail_to_retrieve_staff_details(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.get_store_staff("bakery")
        self.assertFalse(r.success, "error: get staff details action succeeded")
        self.assertEqual(None, r.result, "error: owner got staff details after removed")

    def test_fail_to_add_product(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.add_product("bakery", "lafa", "1", 5, 20, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa found")

    def test_fail_to_update_product_quantity(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.update_product_quantity("bakery", "bread", 50)
        self.assertFalse(r.success, "error: update product quantity action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_name(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_name("bakery", "bread", "new_bread")
        self.assertFalse(r.success, "error: update product quantity action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("new_bread", store, "error: new_bread found")
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_price(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_price("bakery", 10, 30)
        self.assertFalse(r.success, "error: update product price action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_category(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_category("bakery", "bread", "gluten")
        self.assertFalse(r.success, "error: update product price action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_remove_product(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.remove_product("bakery", "bread")
        self.assertFalse(r.success, "error: remove product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_appoint_owner(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.appoint_owner(self.registered_user[0], "bakery")
        self.assertFalse(r.success, "error: appoint owner action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.registered_user[0], appointment)
        self.assertNotIn(self.store_owner1[0], appointment)

    def test_fail_to_appoint_manager(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_owner1)
        r = self.app.appoint_manager(self.registered_user[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.registered_user[0], appointment)
        self.assertNotIn(self.store_owner1[0], appointment)

    def test_fail_to_interact_with_a_customer(self):
        ...

    def test_fail_to_add_rule(self):
        ...

    def test_fail_to_change_discount_policy(self):
        ...

    def test_fail_to_change_purchase_policy(self):
        ...

    def test_fail_to_start_bid(self):
        ...

    def test_fail_to_approve_a_bid(self):
        ...

    def set_store_and_appointments(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.app.logout()
        self.app.login(*self.store_owner1)
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_founder1)
        self.app.remove_appointment(self.store_owner1[0], "bakery")
        self.app.logout()

    def approve_owner(self, owner, approving_list):
        for member in approving_list:
            self.app.login(*member)
            self.app.approve_owner(owner, "bakery")
            self.app.logout()
        