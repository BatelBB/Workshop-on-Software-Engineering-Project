from paymentInterfaces import IExternalPaymentService


class paymentProxy(IExternalPaymentService):
    real: IExternalPaymentService

    def __init__(self, amount: int, buyer: int, seller: int):
        real = None
        super().__init__(amount, buyer, seller)

    def payWIthCreditcard(self, cardNumber, cvv) -> bool:
        if self.real is not None:
            return self.real.payWIthCreditcard(cardNumber, cvv)

        super().success = True
        return True

    def payWIthPaypal(self, username, password) -> bool:
        if self.real is not None:
            return self.real.payWIthPaypal(username, password)

        super().success = True
        return True

