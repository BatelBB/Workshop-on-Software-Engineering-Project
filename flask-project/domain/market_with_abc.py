from abc import ABC as AbstractClass, abstractmethod


class MarketInterface(AbstractClass):
    @abstractmethod
    def boot(self):
        ...


class MarketImpl(MarketInterface):
    def boot(self):
        print("boot")
