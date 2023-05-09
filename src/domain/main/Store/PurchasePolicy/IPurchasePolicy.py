from abc import ABC

import abstract as abstract


# TODO in 2nd version
class IPurchasePolicy(ABC):
    @abstract
    def apply_policy(self):
        ...