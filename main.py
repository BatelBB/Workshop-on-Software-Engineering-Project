from src.domain.main.Market.Market import Market
import json

admin = ('Kfir', 'Kfir')


def run_external_scenario(scenario_path):
    market = Market()
    session = market.enter()

    with open(scenario_path, 'r') as file:
        scenario = json.load(file)

        actions = scenario['actions']
        for a in actions:
            action_name, args = a['action'], a['args']
            session.dispatch(action_name, *args)

    # shutdown system via admin account
    session.login(*admin)
    session.shutdown()


def basic_interaction_with_market():
    market = Market()
    session = market.enter()
    r = session.register("Nir", "")
    # r = session.login("Nir", "marry had a little lambda")
    # r = session.open_store("Amazon")
    # r = session.open_store("Ebay")
    # r = session.open_store("Yahoo")
    # r = session.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123, ['BLAH'])
    # r = session.add_product("Ebay", "Razer Blackwidow V3", "Keyboards", 499.123, 123, ['MOSHE'])
    # r = session.add_product("Yahoo", "Razer Blackwidow V3", "Keyboards", 599.123, 123, ['RBV3'])
    # r = session.get_products_by_category('Keyboards')
    # r = session.get_products_in_price_range(500, 799)
    # r = session.change_product_name("Ebay", "Razer Blackwidow V3", "marry had a little lambda")
    # r = session.get_products_by_name("marry had a little lambda")
    # r = session.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # r = session.add_to_cart("Yahoo", "Razer Blackwidow V3", 555)
    # r = session.add_to_cart("Amazon", "Razer Blackwidow V3", 7) # should increase the quantity to 130
    # r = session.add_to_cart("Ebay", "marry had a little lambda", 7) #
    # r = session.add_to_cart("Ebay", "marry had a little lambda", 7)# should increase the quantity to 14
    # r = session.update_cart_product_quantity("Ebay", "marry had a little lambda", 55)# should increase the quantity to 55
    # r = session.update_cart_product_quantity("Ebay", "marry had a little lambda", 123)# should increase the quantity to 123
    # r = session.change_product_category("Amazon", "Razer Blackwidow V3", "SOoooKAAAAAA")
    # r = session.show_cart()
    # r = session.remove_product_from_cart("Yahoo", "Razer Blackwidow V3")
    # r = session.show_cart()
    # r = session.get_cart()
    # r = session.get_store("Amazon")
    # r = session.get_whole_store("Amazon")
    # r = session.get_store("Yahoo")
    # r = session.get_whole_store("Yahoo")
    session.login(*admin)
    session.shutdown()


if __name__ == '__main__':
    market = Market()
    s0 = market.enter()
    # s0.load_configuration()
    s1 = market.enter()
    s1.register("u1", "p1")
    s1.login("u1", "p1")
    s2 = market.enter()
    s2.register("u2", "p1")
    s2.login("u2", "p1")
    s3 = market.enter()
    s3.register("u3", "p1")
    s3.login("u3", "p1")



    s1.open_store("s1")
    s1.appoint_owner("u2", "s1")
    #
    s1.add_product("s1", "p1", "c1", 100, 50)
    s1.start_bid("s1", "p1")
    s3.purchase_with_non_immediate_policy("s1", "p1", "card", ["1233", "123", "05/2025"], "ben-gurion", "1234", 20, "beer sheva", "israel")
    s1.approve_bid("s1", "p1", True)
    res = s2.approve_bid("s1", "p1", True)

    # s1.appoint_owner("u2", "s1")
    # s1.appoint_owner("u3", "s1")
    # s2.appoint_owner("u3", "s1")

    res = s1.get_store("s1")


    print(3)


    # basic_interaction_with_market()
    # run_external_scenario('States/scenario1.json')
    # run_external_scenario('States/scenario2.json')
