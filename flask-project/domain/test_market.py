from domain.market_with_abc import MarketInterface, MarketImpl

if __name__ == '__main__':
    market: MarketInterface = MarketImpl()
    market.boot()
