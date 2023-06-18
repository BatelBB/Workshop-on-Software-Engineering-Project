import string

from sqlalchemy import Column, String, Integer, Float

from DataLayer.DAL import Base, DAL
from src.domain.main.Utils.OwnersApproval import OwnersApproval
from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService
from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import IProvisionService
from src.domain.main.StoreModule.PurchasePolicy.IPurchasePolicy import IPurchasePolicy
from src.domain.main.Utils.Logger import report, report_error
from src.domain.main.Utils.Response import Response


class BidPolicy(Base):
    __tablename__ = 'bids'
    __table_args__ = {'extend_existing': True}

    store_name = Column("store_name", String, primary_key=True)
    product_name = Column("product_name", String, primary_key=True)
    approval_id = Column("approval_id", Integer, primary_key=True)
    highest_bid = Column("highest_bid", Float)
    payment_details_str = Column("payment_details_str", String, default='')
    holder = Column("holder", String, default='')
    user_id = Column("user_id", String, default='')
    address = Column("address", String, default='')
    postal_code = Column("postal_code", String, default='')
    city = Column("city", String, default='')
    country = Column("country", String, default='')

    def __init__(self, approval: OwnersApproval, store_name, product_name, is_from_db=None):
        self.store_name = store_name
        self.product_name = product_name
        self.approval = approval
        self.approval_id = approval.approval_id
        self.highest_bid = 0
        if is_from_db is not None:
            self.approval.restore()

        self.payment_details = []

        self.payment_details_str = ''
        self.holder = ''
        self.user_id = ''

        self.address = ''
        self.postal_code = ''
        self.city = ''
        self.country = ''

    def apply_policy(self, payment_details, holder, user_id, address, postal_code,
                     city, country, how_much) -> Response[bool]:
        if how_much > self.highest_bid:
            self.highest_bid = how_much
            self.payment_details = payment_details
            self.payment_details_str = ",".join(payment_details)
            self.holder = holder
            self.user_id = user_id
            self.address = address
            self.postal_code = postal_code
            self.city = city
            self.country = country
            DAL.update(self)
            return report("apply_policy->bid highest bidder has been switched", True)

        return report_error("apply_policy", "offer too low")

    def remove_from_approval_dict_in_bid_policy(self, person: str):
        self.approval.remove_owner(person)
        if self.approval.is_approved().result:
            return self.execute()

    def add_to_approval_dict_in_bid_policy(self, person: str):
        self.approval.add_owner(person)

    def execute(self):
        self.is_active = 0
        return Response(self.__dic__(), "bid_ended")

    def approve(self, person: str, is_approve) -> Response:
        if not is_approve:
            self.highest_bid = 0
            self.approval.restore()
            DAL.update(self)
            return report("successfuly declined bid", False)

        res = self.approval.approve(person)
        if not res.result:
            return res
        return self.execute()

    def get_cur_bid(self):
        return self.highest_bid

    @staticmethod
    def create_instance_from_db_query(r):
        store_name, product_name, approval_id, highest_bid, payment_details_str, holder, user_id, address, postal_code, city, country = \
            r.store_name, r.product_name, r.approval_id, r.highest_bid, r.payment_details_str, r.holder, r.user_id, r.address, r.postal_code, r.city, r.country

        approval = DAL.load(OwnersApproval, lambda r: r.approval_id == approval_id,
                            OwnersApproval.create_instance_from_db_query)
        bid = BidPolicy(approval, store_name, product_name)
        bid.highest_bid, bid.payment_details_str, bid.holder, bid.user_id, bid.address, bid.postal_code, bid.city, bid.country = \
            highest_bid, payment_details_str, holder, user_id, address, postal_code, city, country
        bid.payment_details = payment_details_str.split(",")
        return bid

    def delete_from_db(self):
        OwnersApproval.delete_record(self.approval_id)
        BidPolicy.delete_record(self.store_name, self.product_name)

    @staticmethod
    def load_all_bids(store_name):
        out = {}
        for b in DAL.load_all_by(BidPolicy, lambda r: r.store_name == store_name,
                                 BidPolicy.create_instance_from_db_query):
            out[b.product_name] = b
        return out

    def add_to_db(self):
        OwnersApproval.add_record(self.approval)
        BidPolicy.add_record(self)

    @staticmethod
    def add_record(bid):
        DAL.add(bid)

    @staticmethod
    def delete_record(store_name, product_name):
        DAL.delete(BidPolicy, lambda r: r.store_name == store_name and r.product_name == product_name)

    def __dic__(self):
        return {"highest_bid": self.highest_bid, "payment_details": self.payment_details, "holder": self.holder,
                "user_id": self.user_id, "address": self.address, "postal_code": self.postal_code,
                "city": self.city, "country": self.country, "product_name": self.product_name,
                "store_name": self.store_name}
