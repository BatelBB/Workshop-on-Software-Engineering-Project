import string
from abc import ABC, abstractmethod


class IExternalPaymentService(ABC):

    @abstractmethod
    def payWIthCard(self, num:string, cvv: int, exp_date: string, price: float) -> bool:
        ...

    @abstractmethod
    def payWIthPayPal(self, username: string, password: string, price: float) -> bool:
        ...


class ExternalPaymentServciceProxy(IExternalPaymentService):
    real: IExternalPaymentService

    def __init__(self):
        self.real = None

    def payWIthCard(self, num:string, cvv: int, exp_date: string, price: float):
        if self.real is None:
            return True

        return self.real.payWIthCard(num, cvv, exp_date, price)

    def payWIthPayPal(self, username: string, password: string, price: float) -> bool:
        if self.real is None:
            return True

        return self.real.payWIthCard(username, password, price)

