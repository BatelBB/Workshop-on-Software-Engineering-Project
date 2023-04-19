import string
from PaymentServices import IPaymentService, PayWithCard, PayWithPayPal


class PaymentFactory:

    def getPaymentService(self, type: string) -> IPaymentService:
        if type == "card":
            return PayWithCard.__init__()
        elif type == "paypal":
            return PayWithPayPal.__init__()
        else:
            raise Exception("invalid payment option")
