from abc import ABC, abstractmethod
from IProvisionService import IExternalProvisionService, provisionProxy

class IProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, roductID: int, amount: int) -> bool:
        ...




class provisionService(IProvisionService):
    proxy: IExternalProvisionService

    def __init__(self):
        self.proxy = provisionProxy.__init__()

    def getDelivery(self, productID: int, amount: int) -> bool:
        return self.proxy.getDelivery(productID, amount)