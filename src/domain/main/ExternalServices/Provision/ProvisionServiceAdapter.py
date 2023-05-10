import string
from abc import ABC, abstractmethod

from domain.main.ExternalServices.Provision.IProvisionService import IExternalProvisionService, provisionProxy
from domain.main.Utils.Logger import report, Logger, report_error, report_info

class IProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str) -> bool:
        ...




class provisionService(IProvisionService):
    proxy: IExternalProvisionService

    def __init__(self):
        self.proxy = provisionProxy()

    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str) -> bool:
        report("ordered delivery ", True)
        return self.proxy.getDelivery(user_name, shop_name, packageID, address, postal_code)