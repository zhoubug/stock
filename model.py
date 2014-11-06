from collections import defaultdict
import data
import matplotlib.pyplot as plt


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

    @staticmethod
    def get_stock_price(symbol, date):
        df = data.read_history_symble(symbol)
        index = df.index.searchsorted(date)
        day = df.ix[index]
        return day
    
    @staticmethod
    def get_trade_days(start_date, end_date):
        df = data.read_history_symble('SH999999')
        start_i = df.index.searchsorted(start_date)
        end_i = df.index.searchsorted(end_date)
        return df.index[start_i:end_i]

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
    
        
class BaseStrategy:
    def __init__(self):
        self.orders = []

    def add_order(self, sym, timestamp, share, price):
        order = Order(sym, timestamp, share, price)
        self.orders.append(order)

    def initial(self, data):
        """
        calculate indicators you want
        """
        pass
    
    def handle(self, symbol, timestamp, data):
        """
        this method will be called every timestamp
        so make order here
        """
        
    
class BackTester:
    def __init__(self, init_cash, symbols, strategy, start_date, end_date):
        """
        """
        self.portfolio = Portfolio(init_cash)
        self.symbols = symbols
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        data = Market.get_stocks(self.symbols, self.start_date, self.end_date)
        self.strategy.initial(data)
        for sym in self.symbols:
            d = data[sym]
            for i in range(1, len(d.index)):
                self.strategy.handle(sym, i, data)

        self.strategy.orders.sort(key=lambda o: o.timestamp)
        
    def analyse(self, visual=False):
        orders = self.strategy.orders
        trade_days = Market.get_trade_days(self.start_date, self.end_date)
        values = []
        for timestamp in trade_days:
            for order in orders:
                t = order.timestamp
                if t == timestamp:
                    Trader.make_order(self.portfolio, order)
            value = self.portfolio.get_value(timestamp)
            values.append(value)
        
        plt.plot(trade_days, values)
        plt.show()

    def get_orders(self):
        return self.strategy.orders

import datetime

class TestStrategy(BaseStrategy):
    def handle(self, symbol, index, data):
        df = data[symbol]
        timestamps = df.index
        close_today = df.ix[timestamps[index]].close
        close_yest = df.ix[timestamps[index-1]].close
        if close_today / close_yest > 1.03:
            self.add_order(symbol, timestamps[index], 500, close_today)
            if index+5 < len(timestamps):
                sell_timestamp = timestamps[index+5]
            else:
                sell_timestamp = timestamps[-1]
            self.add_order(symbol, sell_timestamp, -500,
                           df.ix[sell_timestamp].close)

if __name__ == '__main__':
    symbols = ['SH600000']
    strategy = TestStrategy()
    start_date = datetime.datetime(2014, 1, 1)
    end_date = datetime.datetime(2014, 11, 1)

    tester = BackTester(10000, symbols, strategy, start_date, end_date)
    tester.run()
    orders = tester.get_orders()
    for order in orders:
        print(order)
    tester.analyse()
