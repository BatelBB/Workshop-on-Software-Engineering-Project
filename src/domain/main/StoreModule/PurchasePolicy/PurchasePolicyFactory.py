from src.domain.main.StoreModule.PurchasePolicy.AuctionPolicy import AuctionPolicy


class PurchasePolicyFactory:
    def get_purchase_policy(self, name: str, args: list):
        if name == "Auction":
            return AuctionPolicy(args[0], args[1])