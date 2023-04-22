

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
    r = sesssion.get_store("Amazon")
    r = sesssion.update_product_quantity("Amazon", "Razer Blackwidow V3", 23)
       # r = sesssion.change_product_name("Amazon", "Razer Blackwidow V3", "Test name")
    # r = sesssion.change_product_price("Amazon", 799.123, 10.1)
    r = sesssion.get_store("Amazon")
    # r = sesssion.show_cart() # supposed to be empty
    # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 2)
    # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # r = sesssion.show_cart()
    # # r = sesssion.add_payment_details_paypal("Name", "Password")
    # r = sesssion.purchase_shopping_cart("paypal", ["user", "password"])
    # r = sesssion.show_cart()  # supposed to be empty
    # r = sesssion.get_store("Amazon")
    #
    # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 5)
    # # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # r = sesssion.show_cart()
    # # r = sesssion.add_payment_details_paypal("Name", "Password")
    # r = sesssion.purchase_shopping_cart("card", ["4580", "322", "20/20"])
    # r = sesssion.show_cart()  # supposed to be empty
    # r = sesssion.get_purchase_history("Amazon")
    # r = sesssion.get_store("Amazon")
    # r = sesssion.close_store("Amazon")
    # r = sesssion.get_store("Amazon")
    # r = sesssion.get_all_stores()



    r = sesssion.logout()

    market.shutdown()