import threading
from abc import ABC


class IConcurrentSingleton(type):
    _instance = None
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(IConcurrentSingleton, cls).__call__(*args, **kwargs)
        return cls._instance


class IAbsractConcurrentSingleton(type):
    __metaclass__ = ABC
    _instance = None
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(IAbsractConcurrentSingleton, cls).__call__(*args, **kwargs)
        return cls._instance
