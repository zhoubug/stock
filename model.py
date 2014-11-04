from collections import defaultdict
import math
import data


class Market:
    cache = {}

    @staticmethod
    def get_stocks(symbols, start_date, end_date):
        stocks = {}
        for symbol in symbols:
            df = data.read_history_symble(symbol)
            start_i = df.index.searchsorted(start_date)
            end_i = df.index.searchsorted(end_date)-1

            stocks[symbol] = df.ix[start_i:end_i]
        return stocks
    

class Trader():
    fees = {'buy': [0.0008], 'sell': [0.0008, 1]}

    @staticmethod
    def make_order(portfolio, order):
        price = order.share*order.price
        if price > 0:     # buy
            fee = Trader.fees['buy']
        else:
            fee = Trader.fees['sell']
        total_fee = 0
        for f in fee:
            if f >= 1:          # fee by order
                total_fee += 1
            else:               # percentage by price
                total_fee += price * f
        total_price = price + total_fee
        
        if total_price > portfolio.cash:
            # no money to buy new stock
            pass
        else:
            portfolio.cash -= total_price
            portfolio.positions[order.symbol] += order.share
    

class Portfolio():
    def __init__(self, init_cash):
        self.cash = init_cash
        self.positions = defaultdict(long)
        self.value = init_cash
        self.history_value = []

        
class Order():
    def __init__(self, symbol, date, share, price):
        self.symbol = symbol
        self.date = date
        self.share = share
        self.price = price


class BaseStrategy:
    def initial(self):
        """
        calculate indicators you want
        """
        pass
    
    def handle(self, timestamp):
        """
        this method will be called every timestamp
        so make order here
        """
        
    

        

if __name__ == '__main__':
    import datetime
    start = datetime.datetime(2011, 1, 1)
    end = datetime.datetime(2011, 1, 31)
    df = Market.get_stocks(['SH600000'], start, end)
