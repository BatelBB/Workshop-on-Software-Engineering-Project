from abc import ABC, abstractmethod


from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from src.domain.main.Utils.Logger import report_error, report



class IPurchasePolicy(ABC):
    payment_service: IPaymentService
    delivery_service: IProvisionService
    price: float
    status = 0

    def pay(self) -> bool:
        return self.payment_service.pay(self.price)

    def order_delivery(self) -> bool:
        return self.delivery_service.getDelivery()

    @abstractmethod
    def apply_policy(self, p_service: IPaymentService, d_service: IProvisionService, how_much: float):
        ...

    def new_day(self):
        pass

    def make_purchase(self):
        is_p_success = self.pay()
        if not is_p_success:
            return report_error("make_purchase", "payment failed")

        is_d_success = self.order_delivery()
        if not is_p_success:
            #TODO: return the money
            return report_error("make_purchase", "delivery failed")

        return report("purchase complete", True)


