from domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from domain.main.Store.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from domain.main.Utils.Logger import report, report_error
from domain.main.Utils.Response import Response


class BidPolicy(IPurchasePolicy):
    highest_bid: float
    to_approve: dict[str, bool]

    def __init__(self):
        self.to_approve = {}
        self.highest_bid = 0

    def apply_policy(self, p_service: IPaymentService, d_service: IProvisionService, how_much: float) -> Response[bool]:
        if how_much > self.highest_bid:
            # TODO: send messages to all people in to_approve
            self.highest_bid = how_much
            self.payment_service = p_service
            self.delivery_service = d_service
            return report("apply_policy->bid highest bidder has been switched", True)

        return report_error("apply_policy", "offer too low")

    def set_approval_dict_in_bid_policy(self, l: list):
        for person in l:
            self.to_approve[person] = False

    def remove_from_approval_dict_in_bid_policy(self, person: str):
        self.to_approve.pop(person)

    def add_to_approval_dict_in_bid_policy(self, person: str):
        # TODO: send messages to person
        self.to_approve[person] = False

    def approve(self, person: str) -> Response:
        self.to_approve[person] = True
        res = self.is_approved()
        if res.success:
            return res
        return report(f"{person} approved bid", True)

    def is_approved(self) -> Response[bool]:
        for p in self.to_approve:
            if not self.to_approve[p]:
                return report(f"is_approved {p} not approved bid yet", True)

        self.payment_service.pay(self.highest_bid)
        self.delivery_service.getDelivery()

        return report("bid ended", True)
