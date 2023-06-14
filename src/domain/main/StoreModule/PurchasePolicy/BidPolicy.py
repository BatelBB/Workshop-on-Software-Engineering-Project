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

    def approve(self, person: str, is_approve) -> Response:
        if not is_approve:
            self.highest_bid = 0
            self.payment_service = None
            self.delivery_service = None
            return report("successfuly declined bid", False)

        res = self.approval.approve(person)
        if not res.result:
            return res
        # TODO: send notification to user in case of faliure
        payment_succeeded = self.payment_service.pay(self.highest_bid)
        if not payment_succeeded:
            return report_error(self.approve.__qualname__, 'failed payment')
        if not self.delivery_service.getDelivery():
            self.payment_service.refund(self.highest_bid)
            return report_error(self.approve.__qualname__, 'failed delivery')

        return report("bid ended", True)

    def get_cur_bid(self):
        return self.highest_bid


