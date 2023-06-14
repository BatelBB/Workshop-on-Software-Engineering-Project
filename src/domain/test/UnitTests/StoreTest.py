import unittest
from threading import Thread
from parameterized import parameterized
from src.domain.main.Market.Market import Market
from src.domain.main.Market.Permissions import Permission, get_default_manager_permissions
from Service.IService.IService import IService
from src.domain.test.UnitTests.RandomInputGenerator import get_random_product, get_random_user


class StoreTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.products = [("Razer Blackwidow V3", "Keyboards", 799.123, 123, ['RB3']),
                         ("Razer Huntsman", "Keyboards", 539.123, 76, ['RH']),
                         ("Apple", "Fruits", 3, 5, ['AP']),
                         ("Watermelon", "Fruits", 6.43, 15, ['WM']),
                         ("Vodka", "Alcohol", 79.99, 51, ['VK']),
                         ("Black Label", "Alcohol", 109.99, 86, ['BL']),
                         ("Cucumber", "Vegetables", 9.99, 251, ['CB'])]
        self.stores = ["Amazon", "ebay", "Mini-Shani"]
        self.users = [("A", "blahblahblah"),
                      ("B", "dahdahdah"),
                      ("Mayer", "marry had a little lambda"),
                      ("foo()", "Azam rules!"),
                      ("boo()", "Barami rules!")]

    def setUp(self) -> None:
        # Note: each test create a new, fresh market with a unique session identifier
        self.service: Market = Market()
        self.session = self.service.enter()
        self.service_admin = ('Kfir', 'Kfir')
        self.session.login(*self.service_admin)

    def tearDown(self) -> None:
        session = self.service.enter()
        session.login(*self.service_admin)
        session.shutdown()
        self.service.clear()

    def register(self, i=0) -> tuple:
        user = self.users[i]
        self.assertTrue(self.session.register(*user).success)
        return user

    def login(self, i=0) -> tuple:
        user = self.users[i]
        self.assertTrue(self.session.login(*user).success)
        return user

    def register_all(self) -> None:
        for i in range(len(self.users)):
            self.register(i)

    def login_all(self) -> None:
        for i in range(len(self.users)):
            self.login(i)

    def create_store_owner(self) -> tuple[tuple, str]:
        self.register()
        owner = self.login()
        store = self.stores[0]
        self.assertTrue(self.session.open_store(store).success)
        return owner, store

    '''
        Sequential Test
    '''
    def test_add_product_to_non_registered_store_fail(self):
        store = "WHATEVER"
        for p in self.products:
            response = self.session.add_product(store, *p)
            self.assertFalse(response.success)

    def test_visitor_add_product_to_registered_store(self):
        store = "WHATEVER"
        self.assertTrue(self.session.open_store(store)) # we are logged in to admin user
        product = self.products[0]
        self.session.logout() # logout admin user -> back to Visitor role
        self.assertFalse(self.session.open_store(store).success)
        self.assertFalse(self.session.add_product(store, *product).success)

    def test_store_owner_add_products_success(self):
        self.register()
        self.login()
        for store in self.stores:
            self.assertTrue(self.session.open_store(store).success)
            for product in self.products:
                self.assertTrue(self.session.add_product(store, *product).success)

    def test_store_owner_add_same_product_success(self):
        self.test_store_owner_add_products_success()
        for store in self.stores:
            for product in self.products:
                product_name, product_initial_quantity = product[0], product[3]
                product_expected_quantity = product_initial_quantity * 2
                self.assertTrue(self.session.add_product(store, *product).success)
                self.assertEqual(self.session.get_amount_of(product_name, store).result, product_expected_quantity)

    def test_store_owner_remove_product_success(self):
        self.test_store_owner_add_products_success()
        for store in self.stores:
            for product in self.products:
                product_name = product[0]
                self.assertTrue(self.session.remove_product(store, product_name).success)
                self.assertEqual(self.session.get_amount_of(product_name, store).result, 0)

    def test_store_owner_update_product_success(self):
        new_quantity = 496351
        self.test_store_owner_add_products_success()
        for store in self.stores:
            for product in self.products:
                product_name = product[0]
                self.assertTrue(self.session.update_product_quantity(store, product_name, new_quantity).success)
                self.assertEqual(self.session.get_amount_of(product_name, store).result, new_quantity)

    def test_store_owner_appoints_visitor_failure(self):
        owner, store = self.create_store_owner()
        for i in range(1, len(self.users)):
            appointee = self.users[i][0]
            r = self.session.appoint_manager(appointee, store)
            self.assertFalse(r.success)

    def test_store_owner_appoints_manager_success(self):
        owner, store = self.create_store_owner()
        for i in range(1, len(self.users)):
            appointee = self.register(i)
            appointee_name = appointee[0]
            r = self.session.appoint_manager(appointee_name, store)
            self.assertTrue(r.success)
        return owner, store

    def test_new_manager_default_permissions_success(self):
        owner, store = self.test_store_owner_appoints_manager_success()
        for i in range(1, len(self.users)):
            manager_name = self.users[i][0]
            r = self.session.permissions_of(store, manager_name)
            self.assertTrue(r.success)
            self.assertEqual(r.result, get_default_manager_permissions())

    def test_store_owner_add_permissions_success(self):
        owner, store = self.test_store_owner_appoints_manager_success()
        for i in range(1, len(self.users)):
            manager_name = self.users[i][0]
            for p in Permission:
                r = self.session.add_permission(store, manager_name, p)
                self.assertTrue(r.success)
                r = self.session.permissions_of(store, manager_name)
                self.assertTrue(r.success)
                self.assertTrue(p in r.result)
        return owner, store

    def test_store_owner_remove_permissions_success(self):
        owner, store = self.test_store_owner_add_permissions_success()
        for i in range(1, len(self.users)):
            manager_name = self.users[i][0]
            for p in Permission:
                r = self.session.remove_permission(store, manager_name, p)
                self.assertTrue(r.success)
                r = self.session.permissions_of(store, manager_name)
                self.assertTrue(r.success)
                self.assertTrue(p not in r.result)

    def test_store_manager_add_product_without_permission_failure(self):
        owner, store = self.test_store_owner_appoints_manager_success()
        for i in range(1, len(self.users)):
            # change active user from owner to manager
            self.login(i)
            for p in self.products:
                r = self.session.add_product(store, *p)
                self.assertFalse(r.success)

    def test_add_product_to_a_close_store_failure(self):
        owner, store = self.test_store_owner_appoints_manager_success()
        r = self.session.close_store(store)
        self.assertTrue(r.success)
        for i in range(1, len(self.users)):
            self.login(i)
            for p in self.products:
                r = self.session.add_product(store, *p)
                self.assertFalse(r.success)
        return owner, store

    def test_add_product_to_a_reopened_store_failure(self):
        owner, store = self.create_store_owner()
        r = self.session.close_store(store)
        self.assertTrue(r.success)
        r = self.session.reopen_store(store)
        self.assertTrue(r.success)
        for p in self.products:
            r = self.session.add_product(store, *p)
            self.assertTrue(r.success)

    def test_appointees_of_success(self):
        owner, store = self.create_store_owner()
        for i in range(1, len(self.users)):
            # in each iteration we appoint new manger and switch to his session
            self.register(i)
            appointee_name = self.users[i][0]
            r = self.session.appoint_manager(appointee_name, store)
            self.assertTrue(r.success)
            r = self.session.add_permission(store, appointee_name, Permission.AppointManager)
            self.login(i)
        self.login(0)  # switch back to owner
        r = self.session.appointees_at(store)
        self.assertTrue(r.success)
        owner_appointees = r.result
        # we expect all appointed managers to be root(=owner) appointees
        for i in range(1, len(self.users)):
            appointee_name = self.users[i][0]
            self.assertTrue(appointee_name in owner_appointees)
        return owner, store

    def test_remove_appointment_success(self):
        # We expect the following appointments tree: A -> B -> Mayer -> foo() -> boo()
        owner, store = self.test_appointees_of_success()
        self.login(1)  # switch to user B
        fired_user_name = self.users[2][0]  # Mayer
        r = self.session.remove_appointment(fired_user_name, store)
        self.assertTrue(r.success)
        s = self.service.enter()
        s.login(*self.users[2])
        r = s.remove_appointment('B', "Amazon")
        self.assertFalse(r.success)
        # we expect B to have zero appointees
        r = self.session.appointees_at(store)
        B_appointees = r.result
        self.assertTrue(r.success)
        self.assertEqual(B_appointees, [])
        self.assertTrue('Mayer' not in B_appointees)
        self.assertTrue('foo()' not in B_appointees)
        self.assertTrue('boo()' not in B_appointees)
        self.login(0)  # switch to user A
        r = self.session.appointees_at(store)
        self.assertTrue('B' in r.result)  # we expect user B to remain manager

    def test_get_store_staff_success(self):
        owner, store = self.test_store_owner_appoints_manager_success()
        r = self.session.get_store_staff(store)
        stuff = r.result
        self.assertEqual(len(stuff), len(self.users))  # expect all users to possess a role at store

    def test_cancel_membership_success(self):
        session = self.service.enter()
        r = session.register("Nir", "marry had a little lambda")
        r = session.login("Nir", "marry had a little lambda")
        r = session.login(*self.service_admin)
        r = session.cancel_membership_of("Nir")
        r = session.login("Nir", "marry had a little lambda")
        self.assertFalse(r.success)