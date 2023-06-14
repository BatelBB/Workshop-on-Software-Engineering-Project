import unittest
from threading import Thread

from parameterized import parameterized

from Service.IService.IService import IService
from src.domain.main.Market.Market import Market
from src.domain.test.UnitTests.RandomInputGenerator import get_random_product, get_random_user, get_random_string


class RobustnessTest(unittest.TestCase):

    number_of_threads = [1, 10, 100]

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
        # self.market = Market()
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
        res = self.session.register(*user)
        if not res.success:
            print("awd")
        self.assertTrue(res.success, f'{user[0]} failed register')
        return user

    def login(self, i=0) -> tuple:
        user = self.users[i]
        self.assertTrue(self.session.login(*user).success)
        return user

    def create_store_owner(self) -> tuple[tuple, str]:
        self.register()
        owner = self.login()
        store = self.stores[0]
        self.assertTrue(self.session.open_store(store).success)
        return owner, store

    '''
        Store Concurrency Tests
    '''

    def start_new_session_and_create_store(self, user, store_name: str, results, index) -> None:
        session = self.service.enter()
        r = session.login(*user)
        r = session.open_store(store_name)
        results[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_thread_open_same_store(self, number_of_threads: int):
        user = self.register()
        store_name = "Jihad"
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_create_store, args=(user, store_name, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(1, len(succeeded_results))
        self.assertEqual(1, self.session.get_number_of_stores())

    def start_new_session_and_create_new_store(self, results, index) -> None:
        session = self.service.enter()
        store_name = get_random_string()
        r = session.login(*self.service_admin)
        r = session.open_store(store_name)
        results[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_thread_open_different_stores(self, number_of_threads):
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_create_new_store, args=(results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, self.session.get_number_of_stores())

    def start_new_session_and_add_product_to_store(self, appointees, store, results, index, product=None):

        if product is None:
            product = get_random_product()
        session = self.service.enter()
        appointee = appointees[index]
        session.login(*appointee)
        r = session.add_product(store, *product)
        self.assertTrue(r.success)
        results[index] = r

    def appoints_owners_of(self, store, number_of_managers, session_id=1):
        appointees = []
        while number_of_managers > 0:
            appointee = get_random_user()
            appointee_name = appointee[0]
            self.session.register(*appointee)
            self.session.appoint_owner(appointee_name, store)
            self.service.approve_as_owner_immediatly(session_id, store, appointee_name)
            appointees.append(appointee)
            number_of_managers -= 1
            print(f'number_of_managers = {number_of_managers}')
        return appointees

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_add_different_products_to_store(self, number_of_threads):
        owner, store = self.create_store_owner()
        appointees = self.appoints_owners_of(store, number_of_threads, self.service.get_active_session_id(owner[0]))
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_add_product_to_store, args=(appointees, store, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, len(self.session.get_all_products_of(store).result))

    # @parameterized.expand(number_of_threads)
    def test_multiple_threads_add_same_product_to_store(self, number_of_threads: int=500):
        owner, store = self.create_store_owner()
        appointees = self.appoints_owners_of(store, number_of_threads, self.service.get_active_session_id(owner[0]))
        product = get_random_product()
        product_name, product_quantity = product[0], product[3]
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_add_product_to_store, args=(appointees, store, results, i, product))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(len(succeeded_results), number_of_threads)
        self.assertEqual(len(self.session.get_all_products_of(store).result), 1)
        self.assertEqual(self.session.get_amount_of(product_name, store).result, number_of_threads * product_quantity)

    def start_new_session_and_appoint_a_manager(self, appointed_store_owner, appointee_name, store_name: str, results, index) -> None:
        session = self.service.enter()
        r = session.login(*appointed_store_owner)
        self.assertTrue(r.success)
        r = session.appoint_manager(appointee_name, store_name)
        results[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_appoint_same_manager(self, number_of_threads: int):
        owner, store = self.create_store_owner()
        appointed_store_owner = self.appoints_owners_of(store, number_of_threads, self.service.get_active_session_id(owner[0]))
        appointee = get_random_user()
        appointee_name = appointee[0]
        self.session.register(*appointee)
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_appoint_a_manager, args=(appointed_store_owner[i], appointee_name, store, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(1, len(succeeded_results))
        # We expect store staff to include owner, appointed store owner, only one appointment of appointee
        self.assertEqual(len(appointed_store_owner) + 2, len(self.session.get_store_staff(store).result))

    def start_new_session_register_and_appoint_a_manager(self, owner, store_name, results, index) -> None:
        session = self.service.enter()
        new_manager = get_random_user()
        r = session.register(*new_manager)
        self.assertTrue(r.success)
        r = session.login(*owner)
        self.assertTrue(r.success)
        appointee_name = new_manager[0]
        r = session.appoint_manager(appointee_name, store_name)
        results[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_appoint_new_manager_to_same_store(self, number_of_threads):
        owner, store = self.create_store_owner()
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_register_and_appoint_a_manager, args=(owner, store, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        # We expect store staff to include owner, only one appointment of appointee
        self.assertEqual(number_of_threads + 1, len(self.session.get_store_staff(store).result))

    '''
        User Concurrency Tests
    '''

    def start_new_session_and_register(self, user, result, index):
        session = self.service.enter()
        r = session.register(*user)
        result[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_register_same_user(self, number_of_threads):
        user = get_random_user()
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_register, args=(user, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(len(succeeded_results), 1)

    def start_new_session_and_login(self, user, result, index):
        session = self.service.enter()
        r = session.login(*user)
        result[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_login_same_user(self, number_of_threads):
        user = get_random_user()
        self.session.register(*user)
        threads = [None] * number_of_threads
        results = [None] * number_of_threads
        for i in range(len(threads)):
            threads[i] = Thread(target=self.start_new_session_and_login, args=(user, results, i))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()
        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(len(succeeded_results), number_of_threads)

    def start_new_session_and_register_login(self, result, index):
        session = self.service.enter()
        user = get_random_user()
        r = session.register(*user)
        self.assertTrue(r.success)
        self.assertTrue(session.is_registered(user[0]))
        r = session.login(*user)
        self.assertTrue(r.success)
        self.assertTrue(session.is_logged_in(user[0]))
        result[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_register_and_login(self, number_of_threads):
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(number_of_threads):
            threads[i] = Thread(target=self.start_new_session_and_register_login, args=(results, i))
            threads[i].start()

        for i in range(number_of_threads):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, self.session.get_number_of_registered_users())
