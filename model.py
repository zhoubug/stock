from collections import defaultdict
import data


class Market:
    cache = {}

    @staticmethod
    def get_stocks(symbols, start_date, end_date):
        stocks = {}
        for symbol in symbols:
            df = Market._get_stock(symbol)
            start_i = df.index.searchsorted(start_date)
            end_i = df.index.searchsorted(end_date)-1

            stocks[symbol] = df.ix[start_i:end_i]
        return stocks

    @staticmethod
    def get_stock_price(symbol, date):
        df = Market._get_stock(symbol)
        index = df.index.searchsorted(date)
        day = df.ix[index]
        return day
    
    @staticmethod
    def get_trade_days(start_date, end_date):
        df = Market._get_stock('SH999999')
        start_i = df.index.searchsorted(start_date)
        end_i = df.index.searchsorted(end_date)
        return df.index[start_i:end_i]

    @staticmethod
    def _get_stock(symbol):
        if symbol not in Market.cache:
            df = data.read_history_symble(symbol)
            Market.cache[symbol] = df

        return Market.cache[symbol]

    
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

    def get_value(self, date):
        value = self.cash
        for sym, share in self.positions.items():
            p = Market.get_stock_price(sym, date)
            value += p.close*share
        return value

    
class Order():
    def __init__(self, symbol, timestamp, share, price):
        self.symbol = symbol
        self.timestamp = timestamp
        self.share = share
        self.price = price

    def __str__(self):
        return '{}: {} {} {}'.format(self.timestamp, self.symbol,
                                     self.share, self.price)
    
        
