from domain.main.Market.Market import Market

def seed(market: Market):
    market.init_admin()
    for username in ("batel", "yuval", "hagai", "nir", "mendi"):
        market.register(0, username, "123456")
    