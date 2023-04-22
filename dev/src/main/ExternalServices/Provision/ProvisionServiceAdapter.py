import string
from abc import ABC, abstractmethod

from dev.src.main.ExternalServices.Provision.IProvisionService import IExternalProvisionService, provisionProxy


class IProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, roductID: int, amount: int) -> bool:
        ...




class provisionService(IProvisionService):
    proxy: IExternalProvisionService

    def __init__(self):
        self.proxy = provisionProxy()
        self.address = "need to add"
        self.postal_code = "need to add"

    def getDelivery(self, productID: int, amount: int) -> bool:
        return self.proxy.getDelivery(productID, amount, self.address, self.postal_code)