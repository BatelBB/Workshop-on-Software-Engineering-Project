import unittest

from parameterized import parameterized

from Service.IService.IService import IService
from src.domain.main.Market.Market import Market
from src.domain.main.Utils.Response import Response


class VisitorTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # Note: each test create a new, fresh market with a unique session identifier
        self.service: IService = Market()
        self.session = self.service.enter()
        self.service_admin = ('Kfir', 'Kfir')

    def tearDown(self) -> None:
        session = self.service.enter()
        session.login(*self.service_admin)
        session.shutdown()
        self.service.clear()

    def test_entrance(self) -> None:
        self.assertTrue(self.session.is_open, "A session should be open (is_open field = True) upon entrance!")

    def test_departure(self) -> None:
        self.session.leave()
        self.assertFalse(self.session.is_open, "A session should be closed (is_open field = False) upon departure!")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_registration(self, username: str, password: str):
        response: Response[bool] = self.session.register(username, password)
        self.assertTrue(response.result, "Register an unregistered user should succeed.")
        self.assertTrue(self.session.is_registered(username), f'{username} should be registered!')

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_register_occupied_username_failure(self, username: str, password: str):
        # register
        self.session.register(username, password)
        self.assertTrue(self.session.is_registered(username), f'{username} should be registered by now.')
        # try to register with same username
        response: Response[bool] = self.session.register(username, password)
        self.assertFalse(response.result, "Register an occupied username should fail.")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_login_registered_user_success(self, username: str, password: str):
        self.session.register(username, password)
        response: Response[bool] = self.session.login(username, password)
        self.assertTrue(response.result)
        self.assertTrue(self.session.is_logged_in(username))

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_login_unregistered_user_failure(self, username: str, password: str):
        response: Response[bool] = self.session.login(username, password)
        self.assertFalse(response.result, "Unregistered user can not be logged in")

    @parameterized.expand([
        ("A", "blahblahblah"),
        ("B", "dahdahdah"),
        ("Mayer", "marry had a little lambda"),
        ("foo()", "Azam rules!"),
        ("boo()", "Barami rules!"),
    ])
    def test_logout_registered_user_success(self, username: str, password: str):
        # register a member
        self.session.register(username, password)
        self.assertTrue(self.session.is_registered(username), f'{username} should be registered by now.')
        # login a member
        self.session.login(username, password)
        self.assertTrue(self.session.is_logged_in(username), f'{username} should be logged in by now.')
        # logout same member
        response: Response[bool] = self.session.logout()
        self.assertFalse(self.session.is_logged_in(username))
        self.assertTrue(response.result)

    def test_logout_visitor_failure(self):
        response: Response[bool] = self.session.logout()
        self.assertFalse(response.result)

    def test_member_logout_twice_failure(self):
        username: str = "Edsger Wybe Dijkstra"
        password: str = "Structured programming"
        # register a member
        self.session.register(username, password)
        self.assertTrue(self.session.is_registered(username), f'{username} should be registered by now.')
        # login a member
        self.session.login(username, password)
        self.assertTrue(self.session.is_logged_in(username), f'{username} should be logged in by now.')
        # logout same member
        self.session.logout()
        self.assertFalse(self.session.is_logged_in(username))
        # logout second time
        response: Response[bool] = self.session.logout()
        self.assertFalse(self.session.is_logged_in(username))
        self.assertFalse(response.result)
