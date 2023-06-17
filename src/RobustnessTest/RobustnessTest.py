import unittest
from threading import Thread

from parameterized import parameterized

from src.domain.main.Market.Market import Market
from src.domain.test.UnitTests.RandomInputGenerator import get_random_product, get_random_user, get_random_string


class RobustnessTest(unittest.TestCase):

    number_of_threads = [10, 50, 100]

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
        self.session.load_configuration()

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

    def open_stores_with_products(self, number_of_products):

        out = list()
        session = self.service.enter()
        r = session.login(*self.service_admin)
        self.assertTrue(self.session.is_logged_in(self.service_admin[0]))

        store_name = get_random_string()
        r = session.open_store(store_name)
        self.assertTrue(self.service.verify_store_consistent(store_name))

        while number_of_products > 0:
            p = get_random_product()
            pname = p[0]
            r = session.add_product(store_name, *p)
            self.assertTrue(self.service.verify_product_integrity(store_name, pname))
            out.append((store_name, p))
            number_of_products -= 1

        return out

    @parameterized.expand(number_of_threads)
    def test_multiple_thread_open_stores_and_adding_products(self, number_of_threads):
        number_of_products = 30
        threads = [None] * number_of_threads

        for i in range(len(threads)):
            threads[i] = Thread(target=self.open_stores_with_products, args=(number_of_products,))
            threads[i].start()
        for i in range(len(threads)):
            threads[i].join()

        self.assertEqual(number_of_products * number_of_threads, self.service.get_number_of_products())

    def start_new_session_and_create_store(self, user, store_name: str, results, index) -> None:
        session = self.service.enter()
        r = session.login(*user)
        r = session.open_store(store_name)
        results[index] = r
        self.assertTrue(self.service.verify_store_consistent(store_name))

    @parameterized.expand(number_of_threads)
    def test_multiple_thread_open_same_store(self, number_of_threads):
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
        self.assertTrue(r.success)
        self.assertTrue(self.service.verify_store_consistent(store_name))
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
        product_name = product[0]
        self.assertTrue(self.service.verify_product_integrity(store, product_name))
        results[index] = r

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
            # print(f'number_of_managers = {number_of_managers}')
        for a in appointees:
            appointee_name = a[0]
            self.assertTrue(self.service.verify_appointment_integrity(appointee_name, store))
        return appointees

    def start_new_session_and_appoint_a_manager(self, appointed_store_owner, appointee_name, store_name: str, results, index) -> None:
        session = self.service.enter()
        r = session.login(*appointed_store_owner)
        self.assertTrue(r.success)
        r = session.appoint_manager(appointee_name, store_name)
        results[index] = r
        self.assertTrue(self.service.verify_appointment_integrity(appointee_name, store_name))

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_appoint_same_manager(self, number_of_threads):
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
        self.assertTrue(self.service.verify_appointment_integrity(appointee_name, store_name))

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
        username = user[0]
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(number_of_threads):
            threads[i] = Thread(target=self.start_new_session_and_register, args=(user, results, i))
            threads[i].start()
        for i in range(number_of_threads):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(1, len(succeeded_results))
        self.assertEqual(1, self.service.get_number_of_registered_users())
        self.assertTrue(self.service.verify_user_consistent(username))

    def start_new_session_and_login(self, user, result, index):
        session = self.service.enter()
        r = session.login(*user)
        result[index] = r
        self.assertTrue(r.success)
        username = user[0]
        self.assertTrue(session.is_logged_in(username))

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
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(1, self.service.get_number_of_registered_users())

    def start_new_session_and_register_login(self, result, index):
        session = self.service.enter()
        user = get_random_user()
        username = user[0]
        r = session.register(*user)
        self.assertTrue(r.success)
        self.assertTrue(self.service.verify_user_consistent(username))
        r = session.login(*user)
        result[index] = r
        self.assertTrue(r.success)
        self.assertTrue(session.is_logged_in(username))

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

    def start_new_session_register_login_add_to_cart(self, data, result, index):
        session = self.service.enter()
        user = get_random_user()
        username = user[0]
        r = session.register(*user)
        self.assertTrue(session.is_registered(username))
        r = session.login(*user)
        self.assertTrue(session.is_logged_in(username))

        for store, product in data:
            product_name, product_quantity = product[0], product[3]
            r = session.add_to_cart(store, product_name, product_quantity)
            self.assertTrue(self.service.verify_item_integrity(product_name, username, store))

        result[index] = r


    @parameterized.expand(number_of_threads)
    def test_multiple_threads_add_to_cart(self, number_of_threads):

        number_of_products = 10
        data = self.open_stores_with_products(number_of_products)
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(number_of_threads):
            threads[i] = Thread(target=self.start_new_session_register_login_add_to_cart, args=(data, results, i))
            threads[i].start()

        for i in range(number_of_threads):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, self.session.get_number_of_registered_users())
        self.assertEqual(number_of_threads * number_of_products, self.service.get_number_of_items())

    def start_new_session_register_login_update_cart(self, data, result, index):
        session = self.service.enter()
        user = get_random_user()
        username = user[0]
        r = session.register(*user)
        self.assertTrue(session.is_registered(username))
        r = session.login(*user)
        self.assertTrue(session.is_logged_in(username))

        for store, product in data:
            product_name, product_original_quantity = product[0], product[3]
            r = session.add_to_cart(store, product_name, product_original_quantity)
            self.assertTrue(self.service.verify_item_integrity(product_name, username, store))
            new_quantity = 1
            r = session.update_cart_product_quantity(store, product_name, new_quantity)
            self.assertTrue(r.success)
            self.assertEqual(self.service.get_cart_item_from_ram(product_name, username, store).quantity, new_quantity)
            self.assertEqual(self.service.get_cart_item_from_db(product_name, username, store).quantity, new_quantity)

        result[index] = r

    @parameterized.expand(number_of_threads)
    def test_multiple_threads_update_cart(self, number_of_threads):

        number_of_products = 3
        data = self.open_stores_with_products(number_of_products)
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(number_of_threads):
            threads[i] = Thread(target=self.start_new_session_register_login_update_cart, args=(data, results, i))
            threads[i].start()

        for i in range(number_of_threads):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, self.session.get_number_of_registered_users())
        self.assertEqual(number_of_threads * number_of_products, self.service.get_number_of_items())


    '''
        Purchase Concurrency Tests
    '''
    def start_new_session_register_login_add_to_cart_and_purchase(self, data, result, index):
        session = self.service.enter()
        user = get_random_user()
        username = user[0]
        r = session.register(*user)
        self.assertTrue(session.is_registered(username))
        r = session.login(*user)
        self.assertTrue(session.is_logged_in(username))

        for store, product in data:
            product_name, product_quantity = product[0], product[3]
            r = session.add_to_cart(store, product_name, product_quantity)
            self.assertTrue(self.service.verify_item_integrity(product_name, username, store))
        r = session.purchase_shopping_cart("card", ["123","12/2023","123"], "address", "123", "city","country")
        self.assertTrue(session.get_cart().result.is_empty())

        result[index] = r

    # @parameterized.expand(number_of_threads)
    def test_concurrent_purchase_shopping_cart(self, number_of_threads=1):
        number_of_products = 10
        data = self.open_stores_with_products(number_of_products)
        threads = [None] * number_of_threads
        results = [None] * number_of_threads

        for i in range(number_of_threads):
            threads[i] = Thread(target=self.start_new_session_register_login_add_to_cart, args=(data, results, i))
            threads[i].start()

        for i in range(number_of_threads):
            threads[i].join()

        succeeded_results = list(filter(lambda response: response.success, results))
        self.assertEqual(number_of_threads, len(succeeded_results))
        self.assertEqual(number_of_threads, self.session.get_number_of_registered_users())


    # @parameterized.expand(number_of_threads)
    # def test_concurrent_pay(self, n_threads):
    #     self.market.register('user', 'password')
    #     self.market.login('user', 'password')
    #     self.market.add_product_to_cart('user', 'store', 'product', 1, n_threads)
    #     self.market.purchase_shopping_cart('user')
    #
    #     def task(market: Market, payment_details: list, holder: str, user_id: int):
    #         market.pay(payment_details, holder, user_id)
    #
    #     threads = [threading.Thread(target=task, args=(self.market, ['card_number', 'cvv', 'mm/yyyy'], 'holder', 1)) for _ in range(n_threads)]
    #     for thread in threads:
    #         thread.start()
    #     for thread in threads:
    #         thread.join()
    #
    #     # Add appropriate assertion here based on your business logic.