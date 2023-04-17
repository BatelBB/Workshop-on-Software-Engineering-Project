import string
from abc import ABC, abstractmethod


class IExternalPaymentService(ABC):
    @abstractmethod
    def payWIthCreditcard(self, cardNumber: string, cvv: string, amount: int) -> bool:
        ...

    @abstractmethod
    def payWIthPaypal(self, username: string, password: string, amount) -> bool:
        ...


class paymentProxy(IExternalPaymentService):
    real: IExternalPaymentService

    def __init__(self):
        real = None
        print("made a payment proxy")

    def payWIthCreditcard(self, cardNumber, cvv, amount) -> bool:
        if self.real is not None:
            return self.real.payWIthCreditcard(cardNumber, cvv, amount)

        super().success = True
        return True

    def payWIthPaypal(self, username, password, amount) -> bool:
        if self.real is not None:
            return self.real.payWIthPaypal(username, password, amount)

        super().success = True
        return True