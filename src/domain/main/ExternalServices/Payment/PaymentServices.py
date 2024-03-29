import re
import string
from abc import ABC, abstractmethod
from src.domain.main.ExternalServices.Payment.ExternalPaymentServices import IExternalPaymentService, \
    ExternalPaymentServiceReal
from src.domain.main.Utils.Logger import report_info, report_error
from src.domain.main.Utils.Response import Response


class IPaymentService(ABC):

    def __init__(self):
        self.amount_payed: float = 0

    @abstractmethod
    def set_information(self, payment_details: list, holder: str, user_id: int) -> Response[bool]:
        ...

    @abstractmethod
    def pay(self, price: float) -> bool:
        ...

    @abstractmethod
    def refund(self, amount_to_refund: float):
        ...


class PaymentService(IPaymentService):
    card_number: int
    cvv: int

    def __init__(self, external_payment_service: IExternalPaymentService):
        super().__init__()
        self.external_payment_service = external_payment_service
        self.card_number = -1
        self.cvv = -1
        self.month = -1
        self.year = -1
        self.holder = ""
        self.user_id = -1

    def check_pattern(self, num: str):
        pattern = r"\d{2}\/\d{4}"
        match = re.match(pattern, num)
        if match:
            return True
        else:
            return False

    def set_information(self, payment_details: list, holder: str, user_id: int) -> Response[bool]:
        if len(payment_details) != 3:
            return report_error("set_information in paywithcard",
                                "invalid payment parameters, excpected card_num: string, "
                                "cvv: string, exp_date: string")
        else:
            self.user_id = user_id
            self.holder = holder
            self.card_number = payment_details[0]
            self.cvv = payment_details[1]
            date = payment_details[2]
            if self.check_pattern(date):
                date = date.split('/')
                self.month = date[0]
                self.year = date[1]
            else:
                return report_error(self.set_information.__qualname__, "Invalid payment details - needs to be mm/yyyy")
            return Response(True, "success")

    def pay(self, price: float):
        self.amount_payed = price
        return self.external_payment_service.payWIthCard(self.card_number, self.cvv, self.month, self.year, self.holder,
                                                         self.user_id)

    def refund(self, amount_to_refund: float):
        return self.external_payment_service.refundToCard()

