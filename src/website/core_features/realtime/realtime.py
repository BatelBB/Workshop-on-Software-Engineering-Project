from datetime import timedelta, datetime
from typing import Set, Dict, Tuple

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from reactivex import interval, Observer
from reactivex.abc import DisposableBase

from src.domain.main.Notifications.notification import Notification
from website.core_features.domain_access.market_access import get_domain_adapter, _get_market

_connected: Set[str] = set()
_observers: Dict[str, Tuple[DisposableBase, ...]] = {}


def init_realtime(app: Flask):
    CORS(app, resources={r"/*": {"origins": "*"}})
    ws = SocketIO(app, cors_allowed_origins="*")

    @ws.on("connect")
    def on_client_connection():
        domain = get_domain_adapter()
        username = domain.username
        if username is None:
            return
        join_room(username)  # username is in room named after them
        _connected.add(username)

        def on_unread_changed(amount: int):
            ws.send({"event_type": "unread_amount_changed", "amount": amount}, to=username)

        res_obs = domain.unread_amount_observable
        if res_obs.success:
            _observers[username] = (
                res_obs.result.subscribe(on_unread_changed),
            )

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
            subscriptions = _observers[username]
            del _observers[username]
            for subscription in subscriptions:
                subscription.dispose()

    # this is for seeing that WebSockets work.
    def on_interval(i: int):
        time = datetime.now().isoformat()
        for username in list(_connected):
            _get_market().notifications.send_from_user('noreply', username, f'Dear {username}, the time now is {time}')

    # interval(timedelta(seconds=10)).subscribe(on_interval)

    return ws
