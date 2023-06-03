from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime


@dataclass_json
@dataclass
class ChatMessage:
    sender_username: str
    recipient_username: str
    content: str
    timestamp: float = None
    msg_id: int = None
    seen: bool = False

    def is_participant(self, username):
        return username in {self.recipient_username, self.sender_username}

    def __post_init__(self):
        self.msg_id = hash((self.recipient_username, self.sender_username, self.timestamp, self.content))
        if self.timestamp is None:
            self.timestamp = datetime.timestamp(datetime.now())
