import string

from paymentInterfaces import IPaymentService
from paymentInterfaces import IExternalPaymentService
import paymentProxy


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

