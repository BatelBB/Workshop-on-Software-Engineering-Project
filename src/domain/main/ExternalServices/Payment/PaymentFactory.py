import string
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService, PayWithCard

class PaymentFactory:

    def getPaymentService(self, payment_type: str) -> IPaymentService:
        if payment_type == "card":
            p = PayWithCard()
            return p
        else:
            raise Exception("invalid payment option")

