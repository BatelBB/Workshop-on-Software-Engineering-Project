import string
from abc import ABC, abstractmethod
from ExternalPaymentServices import IExternalPaymentService, ExternalPaymentServciceProxy


class IPaymentService(ABC):
    external_payment_service: IExternalPaymentService

    def __init__(self):
        self.external_payment_service = ExternalPaymentServciceProxy()

    @abstractmethod
    def set_information(self, **kwargs):
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

    def set_information(self, card_number: string, cvv: int, exp_date: string):
        self.card_number = card_number
        self.cvv = cvv
        self.exp_date = exp_date

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

    def set_information(self, username: string, password: string):
        self.username = username
        self.password = password

    def pay(self, price: float):
        return self.external_payment_service.payWIthPayPal(self.username, self.password, price)
