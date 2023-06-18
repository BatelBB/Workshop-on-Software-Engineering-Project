from Service.bridge.proxy import Proxy
import unittest


class Messages(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.moshe = ("moshe", "password")
        cls.shulamit = ("shulamit", "password")
        cls.not_registered_user = ("usr4", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.moshe)
        self.app.register(*self.shulamit)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_send_message_happy(self):
        self.app.login(*self.moshe)
        r = self.app.send_message(self.shulamit[0], "hi")
        self.assertTrue(r.success, "error: send message action failed")
        self.app.logout()
        self.app.login(*self.shulamit)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(self.shulamit[0], messages[0]["Recipient"], "error: recipient name incorrect")
        self.assertEqual(self.moshe[0], messages[0]["Sender"], "error: sender name incorrect")
        self.assertEqual("User", messages[0]["Sender_type"], "error: sender type incorrect")
        self.assertEqual("hi", messages[0]["Content"], "error: content incorrect")
        self.assertFalse(messages[0]["Seen"], "error: already seen")
        self.app.logout()

    def test_send_message_to_unregistered_user(self):
        self.app.login(*self.moshe)
        r = self.app.send_message(self.not_registered_user[0], "hi")
        self.assertFalse(r.success, "error: send message action succeeded")
        self.app.logout()
        self.app.register(*self.not_registered_user)
        self.app.login(*self.not_registered_user)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(0, len(messages), "error: inbox is not empty for a new member")

    def test_guest_send_message(self):
        r = self.app.send_message(self.shulamit[0], "hi")
        self.assertFalse(r.success, "error: send message action succeeded")
        self.app.login(*self.shulamit)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(0, len(messages), "error: inbox is not empty for a new member")

    def test_get_inbox_empty_inbox(self):
        self.app.login(*self.shulamit)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(0, len(messages), "error: inbox is not empty for a new member")

    def test_get_inbox_guest(self):
        r = self.app.get_inbox()
        self.assertFalse(r.success and r.result, "error: get inbox action succeeded")

    def test_mark_message_read(self):
        self.app.login(*self.moshe)
        r = self.app.send_message(self.shulamit[0], "hi")
        self.assertTrue(r.success, "error: send message action failed")
        self.app.logout()
        self.app.login(*self.shulamit)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        r = self.app.mark_read(messages[0]["Id"])
        self.assertTrue(r.success, "error: mark read action failed")
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(self.shulamit[0], messages[0]["Recipient"], "error: recipient name incorrect")
        self.assertEqual(self.moshe[0], messages[0]["Sender"], "error: sender name incorrect")
        self.assertEqual("User", messages[0]["Sender_type"], "error: sender type incorrect")
        self.assertEqual("hi", messages[0]["Content"], "error: content incorrect")
        self.assertTrue(messages[0]["Seen"], "error: already seen")
        self.app.logout()

    def test_mark_message_read_invalid_message_id(self):
        self.app.login(*self.moshe)
        r = self.app.send_message(self.shulamit[0], "hi")
        self.assertTrue(r.success, "error: send message action failed")
        self.app.logout()
        self.app.login(*self.shulamit)
        r = self.app.mark_read(0)
        self.assertFalse(r.success, "error: mark read action succeeded")
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(self.shulamit[0], messages[0]["Recipient"], "error: recipient name incorrect")
        self.assertEqual(self.moshe[0], messages[0]["Sender"], "error: sender name incorrect")
        self.assertEqual("User", messages[0]["Sender_type"], "error: sender type incorrect")
        self.assertEqual("hi", messages[0]["Content"], "error: content incorrect")
        self.assertFalse(messages[0]["Seen"], "error: already seen")
        self.app.logout()

    def test_mark_message_read_guest(self):
        r = self.app.mark_read(0)
        self.assertFalse(r.success, "error: mark read action succeeded")
        r = self.app.get_inbox()
        self.assertFalse(r.success and r.result, "error: get inbox action succeeded")

    def test_send__and_read_multiple_messages(self):
        self.app.login(*self.moshe)
        for i in range(100):
            r = self.app.send_message(self.shulamit[0], f"hi{i}")
            self.assertTrue(r.success, "error: send message action failed")
        self.app.logout()

        self.app.login(*self.shulamit)
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(100, len(messages), "error: shulamit didn't get 100 messages")
        for i in range(100):
            self.assertEqual(self.shulamit[0], messages[i]["Recipient"], "error: recipient name incorrect")
            self.assertEqual(self.moshe[0], messages[i]["Sender"], "error: sender name incorrect")
            self.assertEqual("User", messages[i]["Sender_type"], "error: sender type incorrect")
            self.assertEqual(f"hi{i}", messages[i]["Content"], "error: content incorrect")
            self.assertFalse(messages[i]["Seen"], "error: already seen")
            r = self.app.mark_read(messages[i]["Id"])
            self.assertTrue(r.success, "error: mark read action failed")
        r = self.app.get_inbox()
        self.assertTrue(r.success, "error: get inbox action failed")
        messages = r.result
        self.assertEqual(100, len(messages), "error: shulamit didn't get 100 messages")
        for i in range(100):
            self.assertEqual(self.shulamit[0], messages[i]["Recipient"], "error: recipient name incorrect")
            self.assertEqual(self.moshe[0], messages[i]["Sender"], "error: sender name incorrect")
            self.assertEqual("User", messages[i]["Sender_type"], "error: sender type incorrect")
            self.assertEqual(f"hi{i}", messages[i]["Content"], "error: content incorrect")
            self.assertTrue(messages[i]["Seen"], "error: already seen")
        self.app.logout()

    def test_store_send_message(self):
        ...
