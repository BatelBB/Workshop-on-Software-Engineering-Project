import string
from abc import ABC, abstractmethod

from requests import Response

from domain.main.ExternalServices.REST_API.RestAPI_Service import RestAPI
from domain.main.Utils.Logger import report_error, report_info


class IExternalPaymentService(ABC):

    @abstractmethod
    def payWIthCard(self, num: int, cvv: int, month: int, year: int, holder: string, id: int) -> bool:
        ...

    @abstractmethod
    def refundToCard(self) -> bool:
        ...

    @abstractmethod
    def checkServiceAvailability(self) -> bool:
        ...


class ExternalPaymentServiceReal(IExternalPaymentService):

    def __init__(self):
        self.real = RestAPI('https://php-server-try.000webhostapp.com/')
        self.transaction_id = -1

    def checkServiceAvailability(self) -> bool:
        checkDic = {"action_type": "handshake"}
        response: Response = self.real.post(checkDic)
        return True if response.ok else False

    def payWIthCard(self, num: int, cvv: int, month: int, year: int, holder: string, user_id: int):
        if self.checkServiceAvailability():
            payDic = {"action_type": "pay",
                      "card_number": str(num),
                      "month": str(month),
                      "year": str(year),
                      "holder": holder,
                      "ccv": str(cvv),
                      "id": str(user_id)}
            response: Response = self.real.post(payDic)
            if response.ok:
                self.transaction_id = response.text
                report_info(self.payWIthCard.__qualname__, "post request for paying with card success!")
                return True
            else:
                report_error(self.payWIthCard.__qualname__, f"post request respond with error {response.status_code}")
                return False
        else:
            report_error(self.payWIthCard.__qualname__, f"Handshake returned error")
            return False

    def refundToCard(self) -> bool:
        if self.checkServiceAvailability():
            refundDic = {"action_type": "cancel_pay",
                         "transaction_id": str(self.transaction_id)}
            response = self.real.post(refundDic)
            if response.status_code:
                report_info(self.refundToCard.__qualname__, "post request for refund to card success!")
                return True
            else:
                report_error(self.refundToCard.__qualname__, f'post request for refund to card failed {response.status_code}')
                return False
        else:
            report_error(self.refundToCard.__qualname__, "handshake failed")
            return False
