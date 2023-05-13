import string
from abc import ABC, abstractmethod

from src.domain.main.ExternalServices.Provision.IProvisionService import IExternalProvisionService, provisionProxy
from src.domain.main.Utils.Logger import report, Logger, report_error, report_info

class IProvisionService(ABC):
    user_name: str
    shop_name: str
    packageID: int
    address: str
    postal_code: str

    @abstractmethod
    def set_info(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str) -> bool:
        ...

    @abstractmethod
    def getDelivery(self):
        ...



class provisionService(IProvisionService):
    proxy: IExternalProvisionService

    def __init__(self):
        self.proxy = provisionProxy()

    def set_info(self, user_name: str, packageID: int, address: str, postal_code: str, shop_name = "market") -> bool:
        self.user_name = user_name
        self.shop_name = shop_name
        self.packageID = packageID
        self.address = address
        self.postal_code = postal_code

        report("set_info", True)
        return True

    def getDelivery(self) -> bool:
        report("ordered delivery ", True)
        return self.proxy.getDelivery(self.user_name, self.shop_name, self.packageID, self.address, self.postal_code)

