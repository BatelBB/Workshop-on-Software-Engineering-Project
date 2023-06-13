from typing import List, Dict, Tuple

from reactivex import Subject, Observable, of
from reactivex.subject import BehaviorSubject
import reactivex.operators as ops

from src.domain.main.Notifications.notification import Notification, NotificationOriginType
from src.domain.main.Utils.Logger import report_error
from src.domain.main.Utils.Response import Response


class _UnreadController:
    def __init__(self):
        self._data: Dict[str, int] = {}
        self._subject: Subject[Tuple[str, int]] = Subject()

    def get(self, username: str):
        if username not in self._data:
            self._data[username] = 0
        return self._data[username]

    def set(self, username: str, amount: int):
        self._data[username] = amount
        self._subject.on_next((username, amount))

    def add(self, username: str, amount: int):
        self.set(username, self.get(username) + amount)

    def amounts_observable_for(self, username: str) -> Observable[int]:
        return of(self.get(username)).pipe(
            ops.concat(self._subject.pipe(
                ops.filter(lambda x: x[0] == username),
                ops.map(lambda x: x[1])
            ))
        )


class NotificationController:
    def __init__(self):
        self._notifications: List[Notification] = []
        self._unread = _UnreadController()

    def _send(self, sender: str, sender_type: NotificationOriginType, recipient: str, content: str):
        self._notifications.append(Notification(recipient, sender, sender_type, content))
        self._unread.add(recipient, 1)

    def send_from_user(self, sending_user: str, recipient: str, content: str):
        self._send(sending_user, NotificationOriginType.User, recipient, content)

    def send_from_store(self, sending_store: str, recipient: str, content: str):
        self._send(sending_store, NotificationOriginType.Shop, recipient, content)

    def get_unread_observable(self, user: str):
        return self._unread.amounts_observable_for(user)

    def get_notifications_for(self, recipient: str):
        return [n for n in self._notifications if recipient == n.recipient]

    def mark_read(self, actor: str, notification_id: int) -> Response[Notification]:
        for n in self._notifications:
            if n.msg_id == notification_id:
                if actor != n.recipient:
                    return report_error("mark_read", "not the recipient")
                if n.seen:
                    return report_error("mark_read", "this message is already marked as read")
                n.seen = True
                self._unread.add(n.recipient, -1)
                return Response(n)
        return report_error("mark_read", "no such message")
