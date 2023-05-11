from domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from domain.main.Store.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from domain.main.Utils.Logger import report, report_error
from domain.main.Utils.Response import Response


class AuctionPolicy(IPurchasePolicy):
    price: float
    duration: int

    def __init__(self, initial_price: float, duration: int):
        self.price = initial_price
        self.duration = duration

    def apply_policy(self, p_service: IPaymentService, d_service: IProvisionService, how_much: float) -> Response[bool]:
        if how_much > self.price:
            self.price = how_much
            self.payment_service = p_service
            self.delivery_service = d_service
            return report("apply_policy->auction highest bidder has been switched", True)
        return report_error("apply_policy", "price too low")


    def new_day(self):
        self.duration -= 1
        if self.duration == 0:
            res = self.make_purchase()
            if res.success:
                self.status = 1
            else:
                # TODO: notify managers
                pass
