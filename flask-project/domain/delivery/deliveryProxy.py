from deliveryInterfaces import IExternalDeliveryService


class deliveryProxy(IExternalDeliveryService):
    real: IExternalDeliveryService

    def __init__(self):
        #self.real = None
        print("made a delivery proxy")

    def getDelivery(self, productID: int, amount: int) -> bool:
        if self.real is not None:
            return self.real.getDelivery(productID, amount)

        return True;