import string
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService, PayWithCard, PayWithPayPal

class PaymentFactory:

    def getPaymentService(self, payment_type: str) -> IPaymentService:
        if payment_type == "card":
            p = PayWithCard()
            return p
        elif payment_type == "paypal":
            p = PayWithPayPal()
            return p
        else:
            raise Exception("invalid payment option")

