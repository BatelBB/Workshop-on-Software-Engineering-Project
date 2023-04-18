from dev.src.test.acceptanceTests.bridge.Bridge import Bridge
from dev.src.test.acceptanceTests.bridge.proxy import proxy
import unittest

class test_guest(unittest.TestCase):
    session_id: int
    app: proxy

    def setUp(self) -> None:
        self.app = proxy()

    def test_enter_market(self):
        self.session_id = self.app.enter_market()
        self.assertGreater(self.session_id, -1, "error entering market!")
