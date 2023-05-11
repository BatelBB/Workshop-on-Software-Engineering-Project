from src.domain.main.Market.Market import Market
from random import randint, sample

electronics = """
פילטר אקווריום
נורית כיבוי
לחצנים
חרצנים
טוסטר משולשים
דגי חשמל
פיורדים
משחת שיניים חשמלית
כיסא תאורה
גגון אלקטרוני
מד לחץ פסיכולוגי
רדיו טייפ
שעון למסדרון
אינטרקום
וילון חשמלי
טוסטר מקבילים
עין אלקטרונית
טוסטר מצולעים
כיסא חשמלי
חיבור בננה
סאב וופרים
שלט למיקרוגל
מנורת לבה עם לבה אורגנית
תנור מקרר
כינור חשמלי
חוט להט
הלוגן
"""

def init_yuvals_store(market: Market):
    yuval = market.enter()
    yuval.login('yuval', '123456')
    yuvals_store_name = "מרתפי אלקטרוניקה"
    yuval.open_store(yuvals_store_name)
    for item in sample(electronics.splitlines(), 10):
        price = randint(10, 150)
        yuval.add_product(yuvals_store_name, item.strip(), "electronics", price, 100, ["electronics", item.strip()])
    yuval.logout()
    yuval.leave()

def init_batel_store(market):
    batel = market.enter()
    batel.login('batel', '123456')
    batels_store_name = 'Selling the stars'
    batel.open_store(batels_store_name)
    # Generated by our friend, Chat-GPT
    batel.add_product(batels_store_name, "Meteorite Necklace", "Jewelry", 59.99, 10, ["Meteorite", "Necklace", "Unique"])
    batel.add_product(batels_store_name, "Galaxy Backpack", "Accessories", 34.99, 20, ["Galaxy", "Backpack", "Space"])
    batel.add_product(batels_store_name, "Constellation Map", "Home Decor", 19.99, 5, ["Constellations", "Map", "Art"])
    batel.add_product(batels_store_name, "Moon Lamp", "Home Decor", 39.99, 15, ["Moon", "Lamp", "Night Light"])
    batel.add_product(batels_store_name, "Sun Hat", "Apparel", 24.99, 30, ["Sun", "Hat", "Beach"])
    batel.add_product(batels_store_name, "Nebula Blanket", "Home Decor", 79.99, 7, ["Nebula", "Blanket", "Cozy"])
    batel.add_product(batels_store_name, "Planet Earrings", "Jewelry", 14.99, 50, ["Planets", "Earrings", "Cute"])
    batel.add_product(batels_store_name, "Astronaut Ice Cream", "Food & Drink", 4.99, 100, ["Astronaut", "Ice Cream", "Snack"])
    batel.add_product(batels_store_name, "Star Projector", "Electronics", 89.99, 8, ["Stars", "Projector", "Night Light"])
    batel.add_product(batels_store_name, "Saturn Backpack", "Accessories", 39.99, 25, ["Saturn", "Backpack", "Space"])
    batel.add_product(batels_store_name, "Rocket Mug", "Home Decor", 12.99, 40, ["Rocket", "Mug", "Coffee"])
    batel.add_product(batels_store_name, "Asteroid Stress Ball", "Toys & Games", 6.99, 50, ["Asteroid", "Stress Ball", "Toy"])
    batel.add_product(batels_store_name, "Solar System Puzzle", "Toys & Games", 29.99, 12, ["Solar System", "Puzzle", "Educational"])
    batel.add_product(batels_store_name, "Alien Keychain", "Accessories", 8.99, 75, ["Alien", "Keychain", "Gift"]) 
    batel.logout()
    batel.leave()


def seed(market: Market):
    market.init_admin()
    for username in ("batel", "yuval", "hagai", "nir", "mendi"):
        market.register(0, username, "123456")
    init_yuvals_store(market)
    init_batel_store(market)

