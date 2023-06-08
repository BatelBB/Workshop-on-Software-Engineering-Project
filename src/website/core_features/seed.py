from src.domain.main.Market.Market import Market
from random import randint, sample

Electronics = """
נורית כיבוי
לחצנים
טוסטר משולשים
פיורדים
משחת שיניים חשמלית
כיסא תאורה
מד לחץ פסיכולוגי
וילון חשמלי
טוסטר מקבילים
עין אלקטרונית
טוסטר מצולעים
כיסא חשמלי
חיבור בננה
סאב וופרים
מנורת לבה עם לבה אורגנית
תנור מקרר
חתול חשמלי
חוט להט
חוט רהט
מנורת נחת
"""


def init_yuvals_store(market: Market):
    yuval = market.enter()
    yuval.login('yuval', '123456')
    yuvals_store_name = "מרתפי אלקטרוניקה"
    yuval.open_store(yuvals_store_name)
    for item in Electronics.splitlines():
        if not item:
            continue
        price = randint(10, 150)
        yuval.add_product(yuvals_store_name, item.strip(), "Electronics", price, 100, ["Electronics", item.strip()])
    yuval.logout()
    yuval.leave()


def init_batel_store(market):
    batel = market.enter()
    batel.login('Batel', '123456')
    batels_store_name = 'Selling the stars'
    batel.open_store(batels_store_name)
    # Generated by our friend, Chat-GPT
    batel.add_product(batels_store_name, "Meteorite Necklace", "Jewelry", 59.99, 10,
                      ["Meteorite", "Necklace", "Unique"])
    batel.add_product(batels_store_name, "Galaxy Backpack", "Accessories", 34.99, 20, ["Galaxy", "Backpack", "Space"])
    batel.add_product(batels_store_name, "Constellation Map", "Home Decor", 19.99, 5, ["Constellations", "Map", "Art"])
    batel.add_product(batels_store_name, "Moon Lamp", "Home Decor", 39.99, 15, ["Moon", "Lamp", "Night Light"])
    batel.add_product(batels_store_name, "Sun Hat", "Apparel", 24.99, 30, ["Sun", "Hat", "Beach"])
    batel.add_product(batels_store_name, "Nebula Blanket", "Home Decor", 79.99, 7, ["Nebula", "Blanket", "Cozy"])
    batel.add_product(batels_store_name, "Planet Earrings", "Jewelry", 14.99, 50, ["Planets", "Earrings", "Cute"])
    batel.add_product(batels_store_name, "Astronaut Ice Cream", "Food & Drink", 4.99, 100,
                      ["Astronaut", "Ice Cream", "Snack"])
    batel.add_product(batels_store_name, "Star Projector", "Electronics", 89.99, 8,
                      ["Stars", "Projector", "Night Light"])
    batel.add_product(batels_store_name, "Saturn Backpack", "Accessories", 39.99, 25, ["Saturn", "Backpack", "Space"])
    batel.add_product(batels_store_name, "Rocket Mug", "Home Decor", 12.99, 40, ["Rocket", "Mug", "Coffee"])
    batel.add_product(batels_store_name, "Asteroid Stress Ball", "Toys & Games", 6.99, 50,
                      ["Asteroid", "Stress Ball", "Toy"])
    batel.add_product(batels_store_name, "Solar System Puzzle", "Toys & Games", 29.99, 12,
                      ["Solar System", "Puzzle", "Educational"])
    batel.add_product(batels_store_name, "Alien Keychain", "Accessories", 8.99, 75, ["Alien", "Keychain", "Gift"])
    batel.logout()
    batel.leave()

def init_batel_store(market):
    batel = market.enter()
    batel.login('Batel', '123456')
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

def init_hagais_store(market):
    hagai = market.enter()
    hagai.login('hagai', '123456')
    hagais_store_name = 'Hagai\'s Store'
    hagai.open_store(hagais_store_name)
    hagai.add_product(hagais_store_name, "Blue T-Shirt", "Apparel", 19.99, 10, ["Blue", "T-Shirt", "Casual"])
    hagai.add_product(hagais_store_name, "Leather Wallet", "Accessories", 49.99, 5, ["Leather", "Wallet", "Classic"])
    hagai.add_product(hagais_store_name, "Wireless Earbuds", "Electronics", 59.99, 8, ["Wireless", "Earbuds", "Bluetooth"])
    hagai.add_product(hagais_store_name, "Sports Watch", "Fitness", 39.99, 15, ["Sports", "Watch", "Waterproof"])

    hagai.add_purchase_simple_rule('Hagai\'s Store', "Blue T-Shirt", "<", 3)
    hagai.add_purchase_complex_rule('Hagai\'s Store', "Sports Watcht", "=", 2, "Wireless Earbuds", ">", 0, "and")

    hagai.add_simple_discount('Hagai\'s Store', "store", 50)

    hagai.logout()
    hagai.leave()

def seed(market: Market):
    market.init_admin()
    for username in ("Batel", "yuval", "hagai", "nir_m.", "mendi"):
        market.register(0, username, "123456")
    init_yuvals_store(market)
    init_batel_store(market)
    init_hagais_store(market)
