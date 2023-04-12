from abc import ABC, abstractmethod


class IPaymentService(ABC):
    amount: int
    buyer: int
    seller: int
    success: bool

    def __init__(self, amount: int, buyer: int, seller: int):
        self.amount = amount
        self.buyer = buyer
        self.seller = seller
        self.success = False

    @abstractmethod
    def payWIthCreditcard(self, cardNumber, cvv) -> bool:
        ...

    @abstractmethod
    def payWIthPaypal(self, username, password) -> bool:
        ...

    def getReceipt(self):
        if self.success:
            return f'successful money transfer by {self.seller} to {self.buyer}'
        else:
            return False


class IExternalPaymentService(ABC):
    @abstractmethod
    def payWIthCreditcard(self, cardNumber, cvv) -> bool:
        ...

    @abstractmethod
    def payWIthPaypal(self, username, password) -> bool:
        ...

