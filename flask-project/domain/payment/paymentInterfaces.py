import string
from abc import ABC, abstractmethod


class IExternalPaymentService(ABC):
    @abstractmethod
    def payWIthCreditcard(self, cardNumber: string, cvv: string, amount: int) -> bool:
        ...

    @abstractmethod
    def payWIthPaypal(self, username: string, password: string, amount) -> bool:
        ...


class IPaymentService(ABC):
    @abstractmethod
    def payWIthCreditcard(self, cardNumber, cvv) -> bool:
        ...

    @abstractmethod
    def payWIthPaypal(self, username, password) -> bool:
        ...

    @abstractmethod
    def getReceipt(self):
        ...




