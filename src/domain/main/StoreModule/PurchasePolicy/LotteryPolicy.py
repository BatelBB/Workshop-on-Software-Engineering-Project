from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from src.domain.main.StoreModule.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from src.domain.main.Utils.Logger import report, report_error
from src.domain.main.Utils.Response import Response
import random


class LotteryPolicy(IPurchasePolicy):
    initial_price: float
    price: float
    lottery_participants: dict[int, list]  # [% winning, who wins]

    def __init__(self, initial_price: float):
        self.initial_price = initial_price
        self.price = initial_price
        self.lottery_participants = {}

    def apply_policy(self, p_service: IPaymentService, d_service: IProvisionService, how_much: float) -> Response[bool]:
        if self.price <= 0:
            return report_error("apply_policy->lottery", "no more patcipants")

        amount_to_pay = min(self.price, how_much)

        res = p_service.pay(amount_to_pay)
        if res:
            self.lottery_participants[self.lottery_participants.__len__()] = [amount_to_pay / self.initial_price,
                                                                              d_service]
        report(f"apply_policy->someone bought {how_much} tickets for product", True)

        self.price -= amount_to_pay
        if self.price == 0:
            return self.pick_winner()

    def pick_winner(self):
        self.is_active = 0
        rnd = random.random()
        cur = 0
        for i in self.lottery_participants.keys():
            cur += self.lottery_participants[i][0]
            if cur >= rnd:
                # he is the winner
                self.lottery_participants[i][1].getDelivery()
                return report(f"lottery ended: {i} won", True)

        return report_error(f"lottery ended:", "something went wrong")
