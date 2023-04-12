from abc import ABC, abstractmethod


class IExternalDeliveryService(ABC):
    @abstractmethod
    def getDelivery(self, productID: int, amount: int) -> bool:
        ...


class IDeliveryService(ABC):
    @abstractmethod
    def getDelivery(self, roductID: int, amount: int) -> bool:
        ...
