import string
from abc import ABC, abstractmethod


class IExternalProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str) -> bool:
        ...



class provisionProxy(IExternalProvisionService):
    real: IExternalProvisionService

    def __init__(self):
        self.real = None

    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str) -> bool:
        if self.real is not None:
            return self.real.getDelivery(user_name, shop_name, packageID, address, postal_code)

        return True