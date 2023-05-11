
from typing import Optional
from flask import session, g
from flask.sessions import SessionMixin

from src.domain.main.Market.Market import Market
from src.domain.main.Service.IService import IService
from src.domain.main.User.User import User
from src.domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Session import Session
from website.core_features.market_access import get_market


_sessions: ConcurrentDictionary[int, Session] = ConcurrentDictionary()

def get_user(s: SessionMixin) -> User:
    return get_market().get_active_user(get_domain_session_id(s)) # type: ignore


def has_bad_session_id(s: SessionMixin) -> bool:
    return ("session_id" in s) and s["session_id"] not in _sessions.dictionary

def get_domain_session_id(s: SessionMixin) -> int:
    if "session_id" not in s or has_bad_session_id(s):
        domain_session = get_market().enter()
        sid = domain_session.identifier
        _sessions.insert(sid, domain_session)
        s["session_id"] = sid
        s["username"] = None
        return sid
    return s["session_id"]

def get_domain_session(s: SessionMixin) -> Session:
    return _sessions.get(get_domain_session_id(s))

def is_logged_in(s: SessionMixin) -> bool:
    return get_username(s) is not None

def get_username(s: SessionMixin) -> Optional[str]:
    return s["username"] if "username" in s else None