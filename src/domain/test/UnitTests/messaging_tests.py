from dataclasses import dataclass
from typing import List
from unittest import TestCase

from reactivex.abc import DisposableBase

from domain.main.Notifications.notification_controller import NotificationController
from util.iter_utils import single


@dataclass
class IntBox:
    value: int


class MessagingTests(TestCase):
    def setUp(self):
        self.notifications = NotificationController()
        self.subscriptions: List[DisposableBase] = []

    def tearDown(self):
        for s in self.subscriptions:
            s.dispose()

    def test_send_from_user_does_not_raise(self):
        self.notifications.send_from_user('yuval', 'batel', 'sup?')

    def test_send_from_store_does_not_throw(self):
        self.notifications.send_from_store('my store', 'yuval', 'please buy something')

    def test_observables_increases(self):
        hagai, mendi = IntBox(0), IntBox(0)
        self._subscribe_to_unread_count('hagai', hagai)
        self._subscribe_to_unread_count('mendi', mendi)

        self.assertEqual(hagai.value, 0)
        self.assertEqual(mendi.value, 0)

        self.notifications.send_from_user('hagai', 'mendi', 'hello')
        self.assertEqual(mendi.value, 1)
        self.assertEqual(hagai.value, 0)

        self.notifications.send_from_user('mendi', 'hagai', 'hello')
        self.assertEqual(mendi.value, 1)
        self.assertEqual(hagai.value, 1)

        self.notifications.send_from_user('mendi', 'hagai', 'hello')
        self.assertEqual(mendi.value, 1)
        self.assertEqual(hagai.value, 2)

        self.notifications.send_from_user('hagai', 'mendi', 'hello')
        self.assertEqual(mendi.value, 2)
        self.assertEqual(hagai.value, 2)

        self.notifications.send_from_store('stuff', 'mendi', 'hello')
        self.assertEqual(mendi.value, 3)
        self.assertEqual(hagai.value, 2)

        self.notifications.send_from_user('stuff', 'hagai', 'hello')
        self.assertEqual(mendi.value, 3)
        self.assertEqual(hagai.value, 3)

    def test_mark_as_read(self):
        nir = IntBox(0)
        self._subscribe_to_unread_count('nir', nir)
        self.assertEqual(nir.value, 0)
        for i in range(0, 10):
            if i % 2 == 0:
                self.notifications.send_from_store('store', 'nir', 'store msg')
            else:
                self.notifications.send_from_user('batel', 'nir', 'hi')
            self.assertEqual(nir.value, 1)
            msg = single(m for m in self.notifications.get_notifications_for('nir') if not m.seen)
            res = self.notifications.mark_read('nir', msg.msg_id)
            self.assertTrue(res.success, res.description)
            self.assertEqual(nir.value, 0)

    def test_mark_as_read_errors(self):
        nir = IntBox(0)
        self._subscribe_to_unread_count('nir', nir)
        self.assertEqual(nir.value, 0)
        res = self.notifications.mark_read('nir', 0)
        self.assertFalse(res.success, 'there should be no such message')
        self.assertEqual(nir.value, 0)
        self.notifications.send_from_user('nir', 'nir', 'Hello, me, how am I doing?')
        self.assertEqual(nir.value, 1)
        msg = single(self.notifications.get_notifications_for('nir'))
        res = self.notifications.mark_read('not nir', msg.msg_id)
        self.assertFalse(res.success, 'should not be authorized to mark nir\'s messages as read')
        self.assertEqual(nir.value, 1)
        res = self.notifications.mark_read('nir', msg.msg_id + 1)
        self.assertFalse(res.success, 'there should be no such message')
        self.assertEqual(nir.value, 1)


    def _subscribe_to_unread_count(self, username: str, box: IntBox) -> None:
        def on_data(x: int):
            box.value = x

        self.subscriptions.append(
            self.notifications.get_unread_observable(username).subscribe(on_data)
        )
