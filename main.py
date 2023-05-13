import string
from datetime import datetime, timedelta
from functools import reduce
from random import random
from typing import Optional
import operator
import random

from dev.src.main.Market.Market import Market
from dev.src.main.Service.IService import IService
from dev.src.main.User.Basket import Basket, Item

def f(x: Optional[int] = 0, y: Optional[datetime] = datetime.now()):
    print(x, y)

def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

def aggregate(*functions, argument, operator):
    return reduce(lambda acc, predicate: operator(acc, predicate(argument)), functions, True)

def logical_and(a1, a2):
    return a1 and a2

def get_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def pr(pairs):
    for store, product in pairs:
        print(f'Store: {store}, {product}')

# Basic interaction with Market
if __name__ == '__main__':
    # start_date = datetime.now()
    # due_date = datetime.now() + timedelta(days=1)
    # print(start_date.strftime("%d/%m/%Y %H:%M:%S"), due_date.strftime("%d/%m/%Y %H:%M:%S"))
    #
    # market: IService = Market()
    # sesssion = market.enter()
    # r = sesssion.register("Nir", "marry had a little lambda")
    # r = sesssion.register("Yossi", "marry had a little lambda")
    # r = sesssion.register("Dani", "marry had a little lambda")
    # r = sesssion.login("Nir", "marry had a little lambda")
    #
    market: IService = Market()
    sesssion = market.enter()
    r = sesssion.register("Nir", "marry had a little lambda")
    r = sesssion.login("Nir", "marry had a little lambda")
    r = sesssion.open_store("Amazon")
    r = sesssion.open_store("Ebay")
    r = sesssion.open_store("Yahoo")
    r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123, ['BLAH'])
    r = sesssion.add_product("Ebay", "Razer Blackwidow V3", "Keyboards", 499.123, 123, ['MOSHE'])
    r = sesssion.add_product("Yahoo", "Razer Blackwidow V3", "Keyboards", 599.123, 123, ['RBV3'])
    # r = sesssion.get_product_by_name("Razer Blackwidow V3")
    # pr(r.result)
    # r = sesssion.get_product_by_category('Keyboards')
    # pr(r.result)
    r = sesssion.get_product_in_price_range(500, 799)
    # # r = sesssion.remove_product("Amazon", "Razer Blackwidow V3")
    # r = sesssion.get_store("Amazon")
    # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # sesssion.add_to_cart("Amazon", "Razer Blackwidow V3", 123)
    # r = sesssion.show_cart()
    # r = sesssion.login("Nir", "marry had a little lambda")
    # r = sesssion.get_store_staff("Amazon")
    # r = sesssion.close_store("Amazon")
    # r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123)
    # r = sesssion.reopen_store("Amazon")
    # r = sesssion.add_product("Amazon", "Razer Blackwidow V3", "Keyboards", 799.123, 123)
    # r = sesssion.remove_appointment("Moshe", "Amazon")
    # r = sesssion.get_store_staff("Amazon")
    # r = sesssion.logout()
    market.shutdown()