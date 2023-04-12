from deliveryInterfaces import IDeliveryService
from deliveryInterfaces import IExternalDeliveryService
import deliveryProxy

class deliveryService(IDeliveryService):
    proxy: IExternalDeliveryService

    def __init__(self):
        self.proxy = deliveryProxy.__init__()

    def getDelivery(self, productID: int, amount: int) -> bool:
        return self.proxy.getDelivery(productID, amount)