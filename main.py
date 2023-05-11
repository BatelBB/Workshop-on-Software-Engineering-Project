from domain.main.Market.Market import Market
from domain.main.Service.IService import IService


# Basic interaction with Market
if __name__ == '__main__':

    service = Market()
    # sesssion = market.enter()
    #
    s1 = service.enter()
    res = s1.register("sus", "rezah")
    re = s1.login("sus", "rezah")
    res = s1.open_store("burekas gedera")
    res = s1.add_product("burekas gedera", "burekas pitriot", "burekasim", 5, 1, ["burekas", "maafe", "bake"])
    res = s1.start_auction("burekas gedera", "burekas pitriot", 2, 1)
    store = service.stores.get("burekas gedera")
    print(store.products_with_special_purchase_policy)

    s2 = service.enter()
    res = s2.register("u2", "p2")
    res = s2.login("u2", "p2")
    res = s2.purchase_with_non_immediate_policy("burekas gedera", "burekas pitriot", "card",
                                                ["4580", "12/2030", "333"],
                                                "beer sheva", "3777777", 30)
    res = s2.add_to_cart("burekas gedera", "burekas pitriot", 1)
    res = s2.purchase_shopping_cart("card", ["4580", "12/2030", "333"],
                                                "beer sheva", "3777777")
    store.new_day()
    #
    # market.shutdown()