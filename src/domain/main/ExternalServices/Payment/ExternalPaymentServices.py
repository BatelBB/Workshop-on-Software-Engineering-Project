import string
from abc import ABC, abstractmethod


class IExternalPaymentService(ABC):

    @abstractmethod
    def payWIthCard(self, num:string, cvv: int, exp_date: string, price: float) -> bool:
        ...

    @abstractmethod
    def payWIthPayPal(self, username: string, password: string, price: float) -> bool:
        ...

    def refundToPaypal(self, username, password, amount_to_refund) -> bool:
        ...

    def refundToCard(self, num, cvv, exp_date, amount_to_refund) -> bool:
        ...


class ExternalPaymentServiceProxy(IExternalPaymentService):
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

    def refundToCard(self, num:string, cvv: int, exp_date: string, amount_to_refund: float) -> bool:
        if self.real is None:
            return True
        return self.real.refundToCard(num, cvv, exp_date, amount_to_refund)

    def refundToPaypal(self, username: string, password: string, amount_to_refund: float) -> bool:
        if self.real is None:
            return True
        return self.real.refundToPaypal(username, password, amount_to_refund)