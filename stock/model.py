from collections import defaultdict
import data
import indicators as ind
from multiprocessing import Process


class Stock:
    def __init__(self, name, symbol, prices):
        self.name = name
        self.symbol = symbol
        self.prices = prices

    def _get_trade_index(self, start_date=None, end_date=None):
        df = self.prices
        if start_date:
            start_i = df.index.searchsorted(start_date)
        else:
            start_i = 0
            
        if end_date:
            end_i = df.index.searchsorted(end_date)
            if end_i < len(df.index) and df.index[end_i] == end_date:
                end_i += 1
        else:
            end_i = len(df.index)
        return start_i, end_i
    
    def get_trade_days(self, start_date=None, end_date=None):
        start_i, end_i = self._get_trade_index(start_date, end_date)
        return self.prices.index[start_i:end_i]

    def get_stock(self, start_date, end_date):
        start_i, end_i = self._get_trade_index(start_date, end_date)
        s = self.prices.ix[start_i:end_i]
        return Stock(self.name, self.symbol, s)

    def get_price(self, date):
        df = self.prices
        index = df.index.searchsorted(date)
        day = df.ix[index]
        return day
    
    def timestamp_index(self, timestamp):
        return self.prices.index.searchsorted(timestamp)

    def timestamps(self):
        return self.prices.index

    def get_price_index(self, index):
        timestamps = self.prices.index
        day = self.prices.ix[timestamps[index]]
        return day

    def get_prices_index(self, start, end):
        timestamps = self.prices.index
        days = self.prices.ix[timestamps[start:end]]
        return days
    
    def get_price_timestamp(self, timestamp):
        day = self.prices.ix[timestamp]
        return day
        
class Market:
    _cache = {}
    _symbols = []
    
    @staticmethod
    def get_stocks(symbols, start_date=None, end_date=None):
        stocks = {}
        for symbol in symbols:
            stocks[symbol] = Market.get_stock(symbol, start_date, end_date)
        return stocks

    @staticmethod
    def get_stock(symbol, start_date=None, end_date=None):
        stock = Market._get_stock(symbol)
        return stock.get_stock(start_date, end_date)
    
    @staticmethod
    def get_stock_price(symbol, date):
        stock = Market._get_stock(symbol)
        return stock.get_price(date)
    
    @staticmethod
    def get_trade_days(start_date, end_date):
        stock = Market._get_stock('SH999999')
        return stock.get_trade_days(start_date, end_date)
    
    @staticmethod
    def get_symbol_list(market=None):
        if not Market._symbols:
            Market._symbols = data.read_symbol_list()
            Market._symbols.sort()
        if market:
            return filter(lambda s: s.startswith(market), Market._symbols)
        else:
            return Market._symbols

    @staticmethod
    def _get_stock(symbol):
        if symbol not in Market._cache:
            df, tokens = data.read_history_symble(symbol)
            stock = Stock(tokens[1], symbol, df)
            Market._cache[symbol] = stock
        return Market._cache[symbol]

    
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
                total_fee += abs(price) * f
        total_price = price + total_fee
        
        if total_price > portfolio.cash:
            # no money to buy new stock
            pass
        else:
            portfolio.cash -= total_price
            portfolio.positions[order.symbol] += order.share
        return total_fee

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
    

class Property():
    k = 252
    
    def __init__(self, series):
        self.values = series
        returns = ind.returnize(series)
        self.cum_return = (returns+1).cumprod()
        self.avg_return = returns.mean()
        self.std_return = returns.std()
        self.sharpe_ratio = ind.sharpe_ratio(returns, Property.k)


class SimTask(Process):
    def __init__(self, simulator):
        self.simulator = simulator

    def run(self):
        self.simulator.run()
        self.simulator.analyse()


class TaskManager():
    pass
