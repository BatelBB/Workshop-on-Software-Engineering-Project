import string
from abc import ABC, abstractmethod


class IExternalProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, productID: int, amount: int, address: string, ) -> bool:
        ...



class provisionProxy(IExternalProvisionService):
    real: IExternalProvisionService

    def __init__(self):
        #self.real = None
        print("made a delivery proxy")

    def getDelivery(self, productID: int, amount: int) -> bool:
        if self.real is not None:
            return self.real.getDelivery(productID, amount)

        return True