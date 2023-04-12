from paymentInterfaces import IExternalPaymentService


class paymentProxy(IExternalPaymentService):
    real: IExternalPaymentService

    def __init__(self):
        real = None

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

