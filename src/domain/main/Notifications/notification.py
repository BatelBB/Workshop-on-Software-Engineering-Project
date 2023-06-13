
from dataclasses import dataclass
from enum import Enum

from datetime import datetime


class NotificationOriginType(Enum):
    User = 'User'
    Shop = 'Shop'


@dataclass
class Notification:
    recipient: str
    sender: str
    sender_type: NotificationOriginType
    content: str
    timestamp: float = None
    msg_id: int = None
    seen: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.timestamp(datetime.now())
        self.msg_id = abs(hash((self.recipient, self.sender, self.sender_type, self.timestamp, self.content)))

    @property
    def is_from_user(self):
        return self.sender_type == NotificationOriginType.User

    @property
    def is_from_store(self):
        return self.sender_type == NotificationOriginType.Shop
