import string
from abc import ABC, abstractmethod


class IExternalProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, productID: int, amount: int, address: string, postal_code: string) -> bool:
        ...



class provisionProxy(IExternalProvisionService):
    real: IExternalProvisionService

    def __init__(self):
        self.real = None

    def getDelivery(self, productID: int, amount: int, address: string, postal_code: string) -> bool:
        if self.real is not None:
            return self.real.getDelivery(productID, amount, address, postal_code)

        return True