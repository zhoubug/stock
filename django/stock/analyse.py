from model import *
import matplotlib.pyplot as plt
import indicators as ind
import numpy as np
import pandas as pd
from sklearn import linear_model
import datetime


class BaseStrategy(object):
    def __init__(self, **kwargs):
        self.orders = []
        self.parameters = kwargs
        
    def add_order(self, sym, timestamp, share, price):
        order = Order(sym, timestamp, share, price)
        self.orders.append(order)

    def initial(self, data):
        """
        this will be called only once
        """
        pass

    def initial_stock(self, symbol, data):
        """
        this will be called for every stock
        """
        pass
    
    def handle(self, symbol, timestamp, data):
        """
        make orders here
        """
        pass

    
class BaseAnalyst(object):
    def __init__(self):
        self.result = {}
        
    def analyse(self, orders, start_date, end_date, benchmark=None):
        pass

    def report(self):
        pass


class Simulator(object):
    def __init__(self, symbols, strategy, start_date, end_date):
        self.strategy = strategy
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.analysts = {}
        
    def run(self):
        stocks = Market.get_stocks(self.symbols,
                                   self.start_date,
                                   self.end_date)
        self.strategy.initial(stocks)
        for sym in self.symbols:
            self.strategy.initial_stock(sym, stocks)

        for sym in self.symbols:
            stock = stocks[sym]
            for i in range(0, len(stock.timestamps())):
                self.strategy.handle(sym, i, stocks)

        self.strategy.orders.sort(key=lambda o: o.timestamp)

    def add_analyst(self, name, analyst):
        self.analysts[name] = analyst

    def remove_analyst(self, name):
        if name in self.analysts:
            del self.analysts[name]

    def clear_analyst(self):
        self.analysts = {}

    def analyse(self):
        for analyst in self.analysts.values():
            analyst.analyse(self.strategy.orders,
                            self.start_date,
                            self.end_date,
                            'SH999999')

    def report(self):
        reports = {}
        for analyst in self.analysts.values():
            reports[analyst.name] = analyst.report()
        return reports
    
    def get_orders(self):
        return self.strategy.orders

    @staticmethod
    def get_benchmark(sym, start_date, end_date):
        bench = Market.get_stock(sym,
                                 start_date,
                                 end_date)
        benchmark = bench.prices['close']
        return benchmark
        
    
class EventProfiler(BaseAnalyst):
    """
    """
    name = "Event Profiler"
    
    def __init__(self, forward=10, backward=10):
        super(EventProfiler, self).__init__()
        self.forward = forward
        self.backward = backward

    def analyse(self, orders, start_date, end_date, benchmark=None):
        orders_buy = [o for o in orders if o.share > 0]
        orders_sell = [o for o in orders if o.share < 0]

        def event_window(orders):
            windows = []
            for order in orders:
                timestamp = order.timestamp
                sym = order.symbol
                stock = Market.get_stock(sym)
                index = stock.timestamp_index(timestamp)
                timestamps = stock.timestamps()
                
                if index < self.backward or (len(timestamps)-index-1) < self.forward:
                    continue

                window = stock.get_prices_index(index-self.backward,
                                                index+self.forward+1)
                close = window['close']
                norm_close = close / close.ix[self.backward] - 1
                windows.append(norm_close.values)
                if not windows:
                    print('no event')
            return np.mean(windows, 0)

        window_buy = event_window(orders_buy) if orders_buy else None
        window_sell = event_window(orders_sell) if orders_sell else None
        self.result['window_buy'] = window_buy
        self.result['window_sell'] = window_sell
        
        # plt.plot(range(-self.backward, self.forward+1), window_buy)
        # plt.axhline(0, color='black')
        # plt.axvline(0, color='black')        
        # plt.show()

        #return histgram for n-day after
        # nforward = 2
        # returns = []
        # for window in windows:
        #     returns.append(window[self.forward+nforward])
            
        # plt.hist(returns, 50)
        # plt.show()
    def report(self):
        window_buy = self.result['window_buy']
        window_sell = self.result['window_sell']
        return window_buy, window_sell
        
class BackTester(BaseAnalyst):
    """
    """
    name = "back tester"
    
    def __init__(self, init_cash=100000):
        """
        """
        super(BackTester, self).__init__()
        self.portfolio = Portfolio(init_cash)
        
    def analyse(self, orders, start_date, end_date, benchmark_sym=None):
        trade_days = Market.get_trade_days(start_date, end_date)
        values = []
        fee = 0
        for timestamp in trade_days:
            for order in orders:
                t = order.timestamp
                if t == timestamp:
                    f = Trader.make_order(self.portfolio, order)
                    fee += f
            value = self.portfolio.get_value(timestamp)
            values.append(value)

        benchmark = None
        if benchmark_sym:
            benchmark = Simulator.get_benchmark(benchmark_sym,
                                                start_date,
                                                end_date)
            
        self.result['days'] = trade_days
        self.result['values'] = pd.Series(values, index=trade_days)
        self.result['benchmark'] = benchmark
        self.result['fee'] = fee
        self.result['trades'] = len(orders)
        
    def report(self):
        timestamps = self.result['days']
        values = self.result['values']
        benchmark = self.result['benchmark']
        if benchmark is not None:
            use_benchmark = True
        else:
            use_benchmark = False
            
        p_portfolio = Property(values)
        if use_benchmark:
            p_benchmark = Property(benchmark)

        # print("The final value of the portfolio is {}".format(values[-1])) 
        # print("detail of the performance of the portfolio")
        # print("{} to {}".format(timestamps[0], timestamps[-1]))

        # print("Sharpe Ratio of Fund: {}".format(p_portfolio.sharpe_ratio))
        # if use_benchmark:
        #     print("Sharpe Ratio of benchmark: {}".format(p_benchmark.sharpe_ratio))

        # # print("Total Return of Fund: {}".format(cum_return[-1]))
        # # if benchmark:
        # #     print("Total Return of benchmark: {}".format(b_cum_return[-1]))
        # print("Standard Deviation of Fund: {}".format(p_portfolio.std_return))
        # if use_benchmark:
        #     print("Standard Deviation of benchmark: {}".format(p_benchmark.std_return))
            
        # print("Average Daily Return of Fund: {}".format(p_portfolio.avg_return))
        # if use_benchmark:
        #     print("Average Daily Return of benchmar: {}".format(p_benchmark.avg_return))

        if use_benchmark:
            return p_portfolio, p_benchmark
        else:
            return p_portfolio
        # plt.plot(timestamps, cum_return)
        # if use_benchmark:
        #     plt.plot(timestamps, b_cum_return)
        #     plt.legend(['Sim', 'Benchmark'])
        # plt.show()
        

def capm(symbol, index, start_date=None, end_date=None, visual=False):
    stock = Market.get_stock(symbol, start_date, end_date)
    bench = Market.get_stock(index, start_date, end_date)
    s = stock.prices
    i = bench.prices
    
    y = s['close']
    y = ind.returnize(y)
    x = i.ix[s.index]['close']
    x = ind.returnize(x)
    X = [[a] for a in x.values]

    regr = linear_model.LinearRegression(fit_intercept=True)

    regr.fit(X[1:], y[1:])
    beta = regr.coef_[0]
    alpha = regr.intercept_

    # if visual:
    #     plt.scatter(x.values, y.values)
    #     plt.plot(X, regr.predict(X), 'r')
    #     plt.show()
    return x.values, y.values, beta, alpha


ANALYSTS = {
    EventProfiler.name: EventProfiler,
    BackTester.name: BackTester
}
