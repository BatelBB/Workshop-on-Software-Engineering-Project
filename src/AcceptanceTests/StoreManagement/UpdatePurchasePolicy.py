from Service.bridge.proxy import Proxy
import unittest


class UpdatePurchasePolicy(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.happy_user1 = ("usr1", "password")
        cls.happy_user2 = ("usr2", "password")
        cls.happy_user3 = ("usr3", "45sdfgs#$%1")
        cls.not_registered_user = ("usr4", "45sdfgs#$%1")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.happy_user1)
        self.app.register(*self.happy_user2)
        self.app.register(*self.happy_user3)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    # def test_approve_bid_happy(self):
    # def test_not_approve_bid(self):
    # def test_approve_bid_accept_higher_bid(self):
    # def test_approve_bid_ignore_lower_bid(self):
    # def test_approve_bid_after_removing_owner_appointment(self):
    # def test_approve_bid_after_removing_owner_permission(self):
    # def test_approve_bid_after_removing_manager_appointment(self):
    # def test_approve_bid_after_removing_manager_permission(self):
    # def test_approve_bid_invalid_product(self):
    # def test_start_bid_invalid_product(self):
    # def test_approve_bid_missing_quantity_product(self):
    # def test_start_bid_missing_quantity_product(self):
    # def test_approve_bid_removed_product(self):
    # def test_start_bid_removed_product(self):
    # def test_approve_bid_closed_store(self):
    # def test_start_bid_closed_store(self):

