

from dev.src.main.Market.Market import Market
from dev.src.main.Service.IService import IService


# Basic interaction with Market
if __name__ == '__main__':

    market: IService = Market()
    sesssion = market.enter()
    r = sesssion.register("Nir", "marry had a little lambda")
    r = sesssion.login("Nir", "marry had a little lambda")
    r = sesssion.login("Nir", "marry had a little lambda")
    r = sesssion.open_store("Amazon")

    r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 10)

    sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 10)




    s2 = market.enter()
    s2.add_to_cart("Amazon", "Razer Blackwidow V3", 3)
    market.show_cart(s2.identifier)



    r2 = s2.register("sus", "rezah")
    r2 = s2.login("sus", "rezah")

    s2.close_store("Amazon")
    s2.get_store("Amazon")

    sesssion.close_store("Amazon")

    s2.get_store("Amazon")
    #
    # s2.open_store("huimazon")
    # r = sesssion.add_product("huimazon", "keychron v2", "Keyboards", 250, 5)
    #
    # market.get_products_by_category(s2.identifier, "Keyboards")

    # r = sesssion.get_store("Amazon")
    # r = sesssion.update_product_quantity("Amazon", "Razer Blackwidow V3", 23)
    # market.get_store(sesssion.identifier, "Amazon")
    # market.purchase_shopping_cart(sesssion.identifier, "card", ["1234", "123", "1234"])
    # sesssion.get_purchase_history("Amazon")
    # market.get_store(sesssion.identifier, "Amazon")
    #
    # s2 = market.enter()
    # r2 = s2.register("sus", "rezah")
    # r2 = s2.login("sus", "rezah")
    # r2 = market.appoint_manager(sesssion.identifier, "sus", "Amazon")
    #
    # r5 = market.get_store_personal(sesssion.identifier, "Amazon")
    #
    # r2 = market.set_personal_permissions(sesssion.identifier, "sus", "Amazon", True)
    #
    # r2 = market.get_store_purchase_history(s2.identifier, "Amazon")
    #
    # r3 = market.shutdown(s2.identifier)

    s3 = market.enter()
    s3.login("admin", "admin")
    r4 = market.shutdown(s3.identifier)


       # r = sesssion.change_product_name("Amazon", "Razer Blackwidow V3", "Test name")
    # r = sesssion.change_product_price("Amazon", 799.123, 10.1)
    # r = sesssion.get_store("Amazon")
    # # r = sesssion.show_cart() # supposed to be empty
    # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 2)
    # # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # # r = sesssion.show_cart()
    # # # r = sesssion.add_payment_details_paypal("Name", "Password")
    # # r = sesssion.purchase_shopping_cart("paypal", ["user", "password"])
    # # r = sesssion.show_cart()  # supposed to be empty
    # # r = sesssion.get_store("Amazon")
    # #
    # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 5)
    # # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # # r = sesssion.show_cart()
    # # # r = sesssion.add_payment_details_paypal("Name", "Password")
    # # r = sesssion.purchase_shopping_cart("card", ["4580", "322", "20/20"])
    # # r = sesssion.show_cart()  # supposed to be empty
    # # r = sesssion.get_purchase_history("Amazon")
    # # r = sesssion.get_store("Amazon")
    # # r = sesssion.close_store("Amazon")
    # # r = sesssion.get_store("Amazon")
    # # r = sesssion.get_all_stores()
    #
    #
    #
    # r = sesssion.logout()
    #
    # market.shutdown()