from abc import ABC, abstractmethod
import string
from IPaymentService import IExternalPaymentService, paymentProxy

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



class paymentService(IPaymentService):
    amount: int
    buyer: int
    seller: int
    success: bool
    proxy: IExternalPaymentService

    def __init__(self, amount: int, buyer: int, seller: int):
        self.amount = amount
        self.buyer = buyer
        self.seller = seller
        self.success = False
        self.proxy = paymentProxy.__init__()


    def payWIthCreditcard(self, cardNumber: string, cvv: string):
        return self.proxy.payWIthCreditcard(cardNumber, cvv, self.amount)

    def payWIthPaypal(self, username: string, password: string):
        return self.proxy.payWIthCreditcard(username, password, self.amount)

    def getReceipt(self):
        if self.success:
            return f'successful money transfer to {self.seller} from {self.buyer} for the amount of {self.amount}'
        else:
            return False