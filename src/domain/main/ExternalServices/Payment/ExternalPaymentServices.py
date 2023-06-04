import string
from abc import ABC, abstractmethod

from requests import Response
from requests.exceptions import Timeout

from src.domain.main.ExternalServices.REST_API.RestAPI_Service import RestAPI
from src.domain.main.Utils.Logger import report_error, report_info


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

    def __init__(self, retry_limit=3, request_timeout=5):
        self.real = RestAPI('https://php-server-try.000webhostapp.com/')
        self.transaction_id = -1
        self.retry_limit = retry_limit
        self.request_timeout = request_timeout

    def checkValidTransactionID(self, transaction_id: int):
        return 10000 <= transaction_id <= 100000

    def handle_request(self, data: dict):
        for _ in range(self.retry_limit):
            try:
                response: Response = self.real.post(data, timeout=self.request_timeout)
                if response.ok:
                    return response
            except Timeout:
                report_error(__name__, f"Request timed out. Retrying...")
        report_error(__name__, f"Request failed after {self.retry_limit} attempts.")
        return None

    def checkServiceAvailability(self) -> bool:
        checkDic = {"action_type": "handshake"}
        response = self.handle_request(checkDic)
        return True if response and response.ok else False

    def payWIthCard(self, num: int, cvv: int, month: int, year: int, holder: string, user_id: int):
        if self.checkServiceAvailability():
            payDic = {"action_type": "pay",
                      "card_number": str(num),
                      "month": str(month),
                      "year": str(year),
                      "holder": holder,
                      "ccv": str(cvv),
                      "id": str(user_id)}
            response: Response = self.handle_request(payDic)
            if response.ok:
                try:
                    new_response = int(response.text)
                except ValueError:
                    report_error(self.payWIthCard.__qualname__, "response text is invalid")
                    return False
                if self.checkValidTransactionID(int(new_response)):
                    self.transaction_id = new_response
                    report_info(self.payWIthCard.__qualname__, "post request for paying with card success!")
                    return True
                else:
                    report_error(self.payWIthCard.__qualname__, "transaction id is incorrect")
                    return False
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
            if response.status_code and response.text.__eq__("1"):
                report_info(self.refundToCard.__qualname__, "post request for refund to card success!")
                return True
            else:
                report_error(self.refundToCard.__qualname__,
                             f'post request for refund to card failed {response.status_code}')
                return False
        else:
            report_error(self.refundToCard.__qualname__, "handshake failed")
            return False
