from domain.main.Market.Market import Market


admin = ('Kfir', 'Kfir')
# Basic interaction with Market
if __name__ == '__main__':
    market = Market()
    # user = User(Market(), 'John Doe', 'john@example.com')
    # session.add(user)
    # session.commit()

    # market: IService = Market()
    sesssion = market.enter()
    r = sesssion.register("Nir", "marry had a little lambda")
    r = sesssion.login("Nir", "marry had a little lambda")
    # r = sesssion.open_store("Amazon")
    # r = sesssion.open_store("Ebay")
    # r = sesssion.open_store("Yahoo")
    # r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123, ['BLAH'])
    # r = sesssion.add_product("Ebay", "Razer Blackwidow V3", "Keyboards", 499.123, 123, ['MOSHE'])
    # r = sesssion.add_product("Yahoo", "Razer Blackwidow V3", "Keyboards", 599.123, 123, ['RBV3'])
    # r = sesssion.get_products_by_category('Keyboards')
    # r = sesssion.get_products_in_price_range(500, 799)
    # r = sesssion.change_product_name("Ebay", "Razer Blackwidow V3", "marry had a little lambda")
    # r = sesssion.get_products_by_name("marry had a little lambda")
    # r = sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # r = sesssion.add_to_cart("Yahoo", "Razer Blackwidow V3", 555)
    # r = sesssion.show_cart()
    # r = sesssion.get_cart()
    # r = sesssion.get_store("Amazon")
    # r = sesssion.get_whole_store("Amazon")
    # r = sesssion.get_store("Yahoo")
    # r = sesssion.get_whole_store("Yahoo")
    #
    sesssion.login(*admin)
    sesssion.shutdown()