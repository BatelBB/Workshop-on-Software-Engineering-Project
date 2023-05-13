from typing import List

from src.domain.main.Store.PurchasePolicy.LotteryPolicy import LotteryPolicy
from domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from src.domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy
from domain.main.Utils.ConcurrentDictionary import ConcurrentDictionary
from src.domain.main.Utils.Response import Response
from src.domain.main.Utils.Logger import report, report_error, report_info
from src.domain.main.Store.Store import Store


class StoreController:

    def __init__(self):
        self.stores: ConcurrentDictionary[str, Store] = ConcurrentDictionary()
    def verify_registered_store(self, store_name: str) -> Response[Store]:
        store = self.stores.get(store_name)
        return report(f'Entered verify register store function', store)

    def verify_store_contains_product(self, calling_method_name: str, store_name: str, product_name: str) -> \
            Response[Store]:
        response = self.verify_registered_store(store_name)
        if response.success:
            store = response.result
            if store.contains_product(product_name):
                return Response(store)
            else:
                return report_error(calling_method_name,
                                    f'Store \'{store_name}\' does not contains Product \'{product_name}\'')
        else:
            return response

    def open_store(self, store_name):
        store = Store(store_name)
        return self.stores.insert(store_name, store), store

    def delete_store(self, store_name: str):
        self.stores.delete(store_name)

    def get_all_stores(self) -> Response[List[Store]]:
        stores = list(self.stores.dictionary.values())
        return report(f"displaying stores: {stores}", stores)

    def get_store_purchase_history(self, store_name: str):
        store = self.stores.get(store_name)
        return report_info(self.get_store_purchase_history.__qualname__, store.get_purchase_history())

    def get_store_products_by_category(self, category:str):
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_category(category)
            if product_dict:
                output[store_name] = product_dict
        report_info("get_products_by_category", f'products: {output}')
        return Response(output)

    def get_store_products_by_name(self, name: str):
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_name(name)
            if product_dict:
                output[store_name] = product_dict
        report_info("get_products_by_name", f'products: {output}')
        return Response(output)

    def get_store_products_by_keywords(self, keywords:list[str]):
        output = {}
        for store_name in self.stores.to_string_keys().split(', '):
            store = self.stores.get(store_name)
            product_dict = store.get_products_by_keywords(keywords)
            if product_dict:
                output[store_name] = product_dict
        report_info("get_products_by_keywords", f'products: {output}')
        return Response(output)

    def start_auction(self,store_name: str, product_name: str, initial_price: float, duration: int):
        res = self.verify_registered_store(store_name)
        if not res.success:
            return res
        store = res.result
        policy = AuctionPolicy(initial_price, duration)
        return store.add_product_to_special_purchase_policy(product_name, policy)

    def start_lottery(self, store_name: str, product_name: str):
        res = self.verify_registered_store(store_name)
        if not res.success:
            return res
        store = res.result
        policy = LotteryPolicy(store.get_product_price(product_name))
        return store.add_product_to_special_purchase_policy(product_name, policy)

    def start_bid(self, store_name: str, product_name: str):
        res = self.verify_registered_store(store_name)
        if not res.success:
            return res
        store = res.result
        policy = BidPolicy()
        return store.add_product_to_bid_purchase_policy(product_name, policy)

    def apply_purchase_policy(self, store_name: str, product_name: str,how_much: float, payment_service: IPaymentService,
                              delivery_service: IProvisionService):
        res = self.verify_registered_store(store_name)
        if not res.success:
            return res
        store = res.result
        res = store.apply_purchase_policy(payment_service, product_name, delivery_service, how_much)

        return res