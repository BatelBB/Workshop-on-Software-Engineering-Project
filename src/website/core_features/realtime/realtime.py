from datetime import timedelta, datetime
from typing import Set, Dict

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from reactivex import interval, Observer

from domain.main.Chat.chat_message import ChatMessage
from website.core_features.domain_access.market_access import get_domain_adapter, _get_market

_connected: Set[str] = set()
_observers: Dict[str, Observer] = {}


def init_realtime(app: Flask):
    CORS(app, resources={r"/*": {"origins": "*"}})
    ws = SocketIO(app, cors_allowed_origins="*")

    @ws.on("connect")
    def on_client_connection():
        username = get_domain_adapter().username
        if username is None:
            return
        join_room(username)  # username is in room named after them
        _connected.add(username)

        def on_message(message: ChatMessage):
            ws.send(message.to_dict(), to=username)

        _observers[username] = get_domain_adapter().all_messages_including_past.subscribe(on_message)

    @ws.on("data")
    def on_client_sent_message(data):
        domain = get_domain_adapter()
        username = domain.username
        if username is None:
            return
        content = data["content"]
        recipient = data["recipient"]
        domain.send_message(recipient, content)
        print('on_client_sent_message', data)

    @ws.on_error_default  # handles all namespaces without an explicit error handler
    def default_error_handler(e: Exception):
        print("WebSocket handler error: ", type(e), e)

    @ws.on("disconnect")
    def on_disconnect():
        username = get_domain_adapter().username
        if username is None:
            return
        if username in _connected:
            _connected.remove(username)
        if username in _observers:
            ob = _observers[username]
            del _observers[username]
            ob.dispose()

    # this is for seeing that WebSockets work.
    def on_interval(i: int):
        for username in list(_connected):
            _get_market().chat.send_noreply(username, f'This is noreply message {i} for {username}')

    interval(timedelta(seconds=10)).subscribe(on_interval)

    return ws
