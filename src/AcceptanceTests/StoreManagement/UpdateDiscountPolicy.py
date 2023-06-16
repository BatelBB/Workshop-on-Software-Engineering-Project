from Service.bridge.proxy import Proxy
import unittest


class Login(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.happy_user1 = ("usr1", "password")
        cls.happy_user2 = ("usr2", "password")
        cls.happy_user3 = ("usr3", "45sdfgs#$%1")
        cls.not_registered_user = ("usr4", "45sdfgs#$%1")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.happy_user1)
        self.app.register(*self.happy_user2)
        self.app.register(*self.happy_user3)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    #
    # ChangeDiscountPolicy = 'Change discount policy'
    #
    # def test_depth_3_discount(self):