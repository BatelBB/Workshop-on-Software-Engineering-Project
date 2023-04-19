import string
from PaymentServices import IPaymentService, PayWithCard, PayWithPayPal

class PaymentFactory:
    @staticmethod
    def getPaymentService(type: string) -> IPaymentService:
        if type == "card":
            return PayWithCard.__init__()
        elif type == "paypal":
            return PayWithPayPal.__init__()
        else:
            raise Exception("invalid payment option")

