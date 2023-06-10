import unittest
from unittest.mock import patch

from src.domain.main.Utils.Response import Response
from Service.IService.IService import IService

from src.domain.main.Market.Market import Market


class PurchaseTest(unittest.TestCase):
    def setUp(self) -> None:
        # Note: each test create a new, fresh market with a unique session identifier
        self.service: IService = Market()
        self.session = self.service.enter()
        self.service_admin = ('Kfir', 'Kfir')
        self.session.login(*self.service_admin)

    def tearDown(self) -> None:
        session = self.service.enter()
        session.login(*self.service_admin)
        session.shutdown()
        self.service.clear()

    def registerAndLoginDefault(self):
        self.session.register("test", "test_pass")
        self.session.login("test", "test_pass")

    def openStoreDefault(self):
        self.session.open_store("IHerb")

    def addProductsDefault(self):
        self.session.add_product("IHerb", "Vitamin A", "Vitamins", 19.9, 20)
        self.session.add_product("IHerb", "Toothpaste", "Hygiene", 21.2, 25)

    def test_purchaseFlow_returnCorrectly(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "Vitamin A", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/4885"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertTrue(response.success)

    def test_purchaseFlow_NonExistingStore_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("Iherb", "Vitamin A", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/4885"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_emptyShoppingCart_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/5885"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_NonExistingProduct_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "NonExistingProduct", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/4885"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_InvalidPaymentMethod_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "Vitamin A", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("invalid_payment_method",
                                                                       ["123", "123", "12/4588"], "ben-gurion", "1234",
                                                                       "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_InvalidPaymentDetails_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "Vitamin A", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["invalid", "details"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_InsufficientProductQuantity_returnError(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "Vitamin A", 21)  # more than the available quantity
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/4885"], "ben-gurion",
                                                                       "1234", "Beersheba", "Israel")
        self.assertFalse(response.result)

    def test_purchaseFlow_ShippingFails_refundIssued(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb", "Vitamin A", 2)

        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=False), \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.refund',
                      return_value=True) as mock_refund:
            response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                                           "ben-gurion", "1234", "beer sheva", "israel")
        # Make sure that the purchase failed
        self.assertFalse(response.result)
        # Make sure that the refund method was called
        mock_refund.assert_called_once()
        mock_refund.assert_called_once_with(39.8)
