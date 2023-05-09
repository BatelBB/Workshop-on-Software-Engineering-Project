import string
from abc import ABC, abstractmethod
from domain.main.ExternalServices.Payment.ExternalPaymentServices import IExternalPaymentService, \
    ExternalPaymentServciceProxy
from domain.main.Utils.Logger import report_info, report_error
from domain.main.Utils.Response import Response


class IPaymentService(ABC):
    external_payment_service: IExternalPaymentService

    def __init__(self):
        self.external_payment_service = ExternalPaymentServciceProxy()

    @abstractmethod
    def set_information(self, payment_details: list) -> Response[bool]:
        ...

    @abstractmethod
    def pay(self, price: float) -> bool:
        ...


class PayWithCard(IPaymentService):
    card_number: string
    cvv: int
    exp_date: string

    def __init__(self):
        super().__init__()
        self.card_number = ""
        self.cvv = -1
        self.exp_date = ""

    def set_information(self, payment_details: list) -> Response[bool]:
        if len(payment_details) != 3:
            return report_error("set_information in paywithcard",
                                "invalid payment parameters, excpected card_num: string, "
                                "cvv: string, exp_date: string")
        else:
            self.card_number = payment_details[0]
            self.cvv = payment_details[1]
            self.exp_date = payment_details[2]
            return Response(True, "success")

    def pay(self, price: float):
        return self.external_payment_service.payWIthCard(self.card_number, self.cvv, self.exp_date, price)


class PayWithPayPal(IPaymentService):
    username: string
    password: string

    def __init__(self):
        super().__init__()
        self.username = ""
        self.cvv = -1
        self.exp_date = ""

    def set_information(self, payment_details: list) -> Response[bool]:
        if len(payment_details) != 2:
            return report_error("set_information in paywithcard",
                                "invalid payment parameters, excpected username: string, "
                                "password: string")
        else:
            self.username = payment_details[0]
            self.password = payment_details[1]
            return Response(True, "success")

    def pay(self, price: float):
        return self.external_payment_service.payWIthPayPal(self.username, self.password, price)
