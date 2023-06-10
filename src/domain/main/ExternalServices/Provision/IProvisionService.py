import string
from abc import ABC, abstractmethod

from src.domain.main.ExternalServices.REST_API.RestAPI_Service import RestAPI
from src.domain.main.Utils.Logger import report_error, report_info


class IExternalProvisionService(ABC):
    @abstractmethod
    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str, country: str,
                    city: str) -> bool:
        ...

    @abstractmethod
    def cancelDelivery(self):
        ...

    @abstractmethod
    def checkServiceAvailability(self):
        ...


class provisionReal(IExternalProvisionService):

    def __init__(self):
        self.real = RestAPI('https://php-server-try.000webhostapp.com/')
        self.transaction_id = -1

    def checkValidTransactionID(self, transaction_id: int):
        return 10000 <= transaction_id <= 100000

    def checkServiceAvailability(self) -> bool:
        checkDic = {"action_type": "handshake"}
        response = self.real.post(checkDic)
        return True if response.ok else False

    def getDelivery(self, user_name: str, shop_name: str, packageID: int, address: str, postal_code: str, country: str,
                    city: str) -> bool:
        if self.checkServiceAvailability():
            supplyDic = {"action_type": "supply",
                         "name": user_name,
                         "address": address,
                         "city": city,
                         "country": country,
                         "zip": postal_code
                         }
            response = self.real.post(supplyDic)
            if response.ok:
                try:
                    new_response = int(response.text)
                except ValueError:
                    report_error(self.getDelivery.__qualname__, "response text is invalid")
                    return False
                if self.checkValidTransactionID(int(new_response)):
                    self.transaction_id = new_response
                    report_info(self.getDelivery.__qualname__, "post request for sending delivery success!")
                    return True
                else:
                    report_error(self.getDelivery.__qualname__, "transaction id is incorrect")
                    return False
            else:
                report_error(self.getDelivery.__qualname__, f'post request failed - {response.status_code}')
                return False
        else:
            report_error(self.getDelivery.__qualname__, f'handshake failed ')
            return False

    def cancelDelivery(self):
        if self.checkServiceAvailability():
            cancelSupplyDic = {"action_type": "cancel_supply",
                               "transaction_id": self.transaction_id}
            response = self.real.post(cancelSupplyDic)
            if response.ok and response.text.__eq__(1):
                report_info(self.cancelDelivery.__qualname__, f'post request for canceling delivery successes!')
                return True
            else:
                report_error(self.cancelDelivery.__qualname__,
                             f'post request for canceling delivery failed - {response.status_code}')
        else:
            report_error(self.cancelDelivery.__qualname__, "handshake failed")
            return False
