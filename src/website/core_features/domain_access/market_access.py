from multiprocessing import RLock
from typing import Optional

from domain.main.Market.Market import Market
from website.core_features.seed import seed

_lock = RLock()
_instance: Optional[Market] = None


def get_market() -> Market:
    global _instance
    global _lock
    with _lock:
        if _instance is None:
            _instance = Market()
            seed(_instance)
        return _instance
