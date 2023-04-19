

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
    r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123)
    r = sesssion.get_store("Amazon")
    r = sesssion.show_cart() # supposed to be empty
    sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    r = sesssion.show_cart()
    r = sesssion.logout()

    market.shutdown()