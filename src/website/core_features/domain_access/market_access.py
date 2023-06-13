from multiprocessing import RLock
from typing import Optional

from flask import session, flash

from src.domain.main.Market.Market import Market
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from website.core_features.domain_access.session_adapter import SessionAdapter

_lock = RLock()
_instance: Optional[Market] = None


def _get_market() -> Market:
    global _instance
    global _lock
    with _lock:
        if _instance is None:
            _instance = Market()
        return _instance


_sessions: ConcurrentDictionary[int, SessionAdapter] = ConcurrentDictionary()


def has_bad_session_id() -> bool:
    return ("session_id" in session) and session["session_id"] not in _sessions.dictionary


def get_domain_session_id() -> int:
    if "session_id" not in session or has_bad_session_id():
        domain_session = _get_market().enter()
        flash("You've just entered the market. Welcome!")
        sid = domain_session.identifier
        _sessions.insert(sid, SessionAdapter(domain_session))
        session["session_id"] = sid
        session["username"] = None
        return sid
    return session["session_id"]


def get_domain_adapter() -> SessionAdapter:
    return _sessions.get(get_domain_session_id())


def is_logged_in() -> bool:
    return get_username() is not None


def get_username() -> Optional[str]:
    return session["username"] if "username" in session else None
