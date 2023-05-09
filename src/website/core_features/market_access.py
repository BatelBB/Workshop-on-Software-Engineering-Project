from website.core_features.seed import seed
from flask import g
from domain.main.Market.Market import Market


def get_market() -> Market:
    if not hasattr(g, "market"):
        market = Market()
        seed(market)
        setattr(g, "market", market)
    return g.market
