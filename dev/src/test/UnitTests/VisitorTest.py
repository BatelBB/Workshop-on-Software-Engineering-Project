import unittest

from dev.src.main.Market.Market import Market
from dev.src.main.Service.IService import IService
from parameterized import parameterized

from dev.src.main.Utils.Response import Response


# TODO: replace parameterized arguemnts with JSON file for test

class VisitorTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # Note: each test create a new, fresh market with a unique session identifier
        self.serivce: IService = Market()
        self.sesssion = self.serivce.enter()

    def tearDown(self) -> None:
        self.serivce.shutdown()

    def test_entrance(self) -> None:
        self.assertTrue(self.sesssion.is_open, "A session should be open (is_open field = True) upon entrance!")

    def test_departure(self) -> None:
        self.sesssion.leave()
        self.assertFalse(self.sesssion.is_open, "A session should be closed (is_open field = False) upon departure!")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_registration(self, username: str, password: str):
        response: Response[bool] = self.sesssion.register(username, password)
        self.assertTrue(response.result, "Register an unregistered user should succeed.")
        self.assertTrue(self.sesssion.is_registered(username), f'{username} should be registered!')

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_register_occupied_username_failure(self, username: str, password: str):
        # register
        self.sesssion.register(username, password)
        self.assertTrue(self.sesssion.is_registered(username), f'{username} should be registered by now.')
        # try to register with same username
        response: Response[bool] = self.sesssion.register(username, password)
        self.assertFalse(response.result, "Register an occupied username should fail.")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_login_registered_user_success(self, username: str, password: str):
        self.sesssion.register(username, password)
        response: Response[bool] = self.sesssion.login(username, password)
        self.assertTrue(response.result)
        self.assertTrue(self.sesssion.is_logged_in(username))

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_login_unregistered_user_failure(self, username: str, password: str):
        response: Response[bool] = self.sesssion.login(username, password)
        self.assertFalse(response.result, "Unregistered user can not be logged in")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_login_already_logged_in_member_failure(self, username: str, password: str):
        # register a member
        self.sesssion.register(username, password)
        self.assertTrue(self.sesssion.is_registered(username), f'{username} should be registered by now.')
        # login a member
        self.sesssion.login(username, password)
        self.assertTrue(self.sesssion.is_logged_in(username), f'{username} should be logged in by now.')
        # login again same member
        response: Response[bool] = self.sesssion.login(username, password)
        self.assertFalse(response.result)
        self.assertTrue(self.sesssion.is_logged_in(username))

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_logout_registered_user_success(self, username: str, password: str):
        # register a member
        self.sesssion.register(username, password)
        self.assertTrue(self.sesssion.is_registered(username), f'{username} should be registered by now.')
        # login a member
        self.sesssion.login(username, password)
        self.assertTrue(self.sesssion.is_logged_in(username), f'{username} should be logged in by now.')
        # logout same member
        response: Response[bool] = self.sesssion.logout()
        self.assertFalse(self.sesssion.is_logged_in(username))
        self.assertTrue(response.result)

    def test_logout_visitor_failure(self):
        response: Response[bool] = self.sesssion.logout()
        self.assertFalse(response.result)

    def test_member_logout_twice_failure(self):
        username: str = "Edsger Wybe Dijkstra"
        password: str = "Structured programming"
        # register a member
        self.sesssion.register(username, password)
        self.assertTrue(self.sesssion.is_registered(username), f'{username} should be registered by now.')
        # login a member
        self.sesssion.login(username, password)
        self.assertTrue(self.sesssion.is_logged_in(username), f'{username} should be logged in by now.')
        # logout same member
        self.sesssion.logout()
        self.assertFalse(self.sesssion.is_logged_in(username))
        # logout second time
        response: Response[bool] = self.sesssion.logout()
        self.assertFalse(self.sesssion.is_logged_in(username))
        self.assertFalse(response.result)
