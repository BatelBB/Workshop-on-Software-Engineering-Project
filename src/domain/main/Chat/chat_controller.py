from typing import List, Iterable

from domain.main.Chat.chat_message import ChatMessage
from reactivex.subject import ReplaySubject
from reactivex import Observable, Subject
from datetime import datetime

from util.ensure_never_twice import NeverTwice

_never_twice = NeverTwice()

NOREPLY_USERNAME = 'noreply'


class ChatController:
    def __init__(self):
        _never_twice()
        self._messages: List[ChatMessage] = []

        # a subject is an observable where you can use .on_next to trigger all subscribers.
        self._subject: Subject[ChatMessage] = Subject()

        #  a replay subject gets the subscriber everything that was ever sent.
        replay = ReplaySubject()

        # pipe all subject messages to replay subject.
        self._subject.subscribe(on_next=replay.on_next)

        # as a field, I only care that this implements Observable.
        # I don't want to "remember" that it's a subject, because a subject
        # can publish its own messages, and we already took care of
        # how this shows messages.
        self._replay_observable: Observable[ChatMessage] = replay

    @property
    def all_messages_including_past(self) -> Observable[ChatMessage]:
        """
        when you subscribe to this, you'll immediately get all past messages,
        and then start getting new messages.
        """
        return self._replay_observable

    @property
    def new_messages(self) -> Observable[ChatMessage]:
        """
        When you subscribe to this, you'll start getting messages that were
        emitted after you subscribed.
        """
        return self._subject

    def get_past_messages_with(self, username: str) -> List[ChatMessage]:
        return [msg for msg in self._messages if msg.is_participant(username)]

    def send(self, sender_username: str, recipient_username: str, content: str):
        msg = ChatMessage(sender_username=sender_username, recipient_username=recipient_username,
                          content=content)
        print('send-message', msg)
        self._messages.append(msg)
        self._subject.on_next(msg)

    def send_noreply(self, recipient_username: str, content: str):
        self.send(NOREPLY_USERNAME, recipient_username, content)
