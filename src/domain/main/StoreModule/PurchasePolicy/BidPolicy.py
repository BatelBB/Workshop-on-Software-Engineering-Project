from domain.main.Utils.OwnersApproval import OwnersApproval
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from src.domain.main.StoreModule.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from src.domain.main.Utils.Logger import report, report_error
from src.domain.main.Utils.Response import Response


class BidPolicy(IPurchasePolicy):
    highest_bid: float

    def __init__(self, approval: OwnersApproval):
        self.approval = approval
        self.highest_bid = 0

    def apply_policy(self, p_service: IPaymentService, d_service: IProvisionService, how_much: float) -> Response[bool]:
        if how_much > self.highest_bid:
            # TODO: send messages to all people in to_approve
            self.highest_bid = how_much
            self.payment_service = p_service
            self.delivery_service = d_service
            return report("apply_policy->bid highest bidder has been switched", True)

        return report_error("apply_policy", "offer too low")

    def remove_from_approval_dict_in_bid_policy(self, person: str):
        self.approval.remove_owner(person)

    def add_to_approval_dict_in_bid_policy(self, person: str):
        self.approval.add_owner(person)

    def approve(self, person: str) -> Response:
        res = self.approval.approve(person)
        if not res.result:
            return res
        self.payment_service.pay(self.highest_bid)
        self.delivery_service.getDelivery()

        return report("bid ended", True)


