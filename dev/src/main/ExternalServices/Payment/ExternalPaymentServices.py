import string
from abc import ABC, abstractmethod


class IExternalPaymentService(ABC):

    @abstractmethod
    def payWIthCard(self, num:string, cvv: int, exp_date: string) -> bool:
        ...

    @abstractmethod
    def payWIthPayPal(self, username: string, password: string) -> bool:
        ...


class ExternalPaymentServciceProxy(IExternalPaymentService):
    real: IExternalPaymentService

    def __init__(self):
        self.real = None

    def payWIthCard(self, num:string, cvv: int, exp_date: string):
        if self.real is None:
            return True

        return self.real.payWIthCard(num, cvv, exp_date)

    def payWIthPayPal(self, username: string, password: string) -> bool:
        if self.real is None:
            return True

        return self.real.payWIthCard(username, password)

