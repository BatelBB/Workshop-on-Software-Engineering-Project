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

    def test_retrieve_purchase_history(self):
    def test_retrieve_staff_details(self):

    def test_interact_with_customer(self):
    def test_(self):

        RetrievePurchaseHistory = 'Retrieve store purchase history'
        RetrieveStaffDetails = 'Retrieve store staff details'
        InteractWithCustomer = 'Get and answer customer questions'
        Add = 'Add a Product'
        AddRule = 'Add a Store-Role'
        Update = 'Update product details'
        Remove = 'Remove product'
        ChangeDiscountPolicy = 'Change discount policy'
        ChangePurchasePolicy = 'Change purchase policy'
        AppointManager = 'Appoint another manager'
        AppointOwner = 'Appoint another owner'
        CancelManagerAppointment = 'Cancel appointment of another manager'
        CancelOwnerAppointment = 'Cancel appointment of another owner'
        CloseStore = 'Close store'
        ReopenStore = 'Reopen store'
        OpenStore = 'Open store'
        OpenAuction = 'Open Auction'
        OpenLottery = 'Open Lottery'
        StartBid = 'Start a bid'
        ApproveBid = 'Approve a bid'