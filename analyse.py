from model import *
import matplotlib.pyplot as plt
import indicators as ind
import numpy as np
import pandas as pd
from sklearn import linear_model

class BaseStrategy(object):
    def __init__(self):
        self.orders = []

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
    def __init__(self, symbols, strategy, start_date, end_date):
        self.strategy = strategy
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        
    def run(self):
        data = Market.get_stocks(self.symbols, self.start_date, self.end_date)
        self.strategy.initial(data)
        for sym in self.symbols:
            self.strategy.initial_stock(sym, data)

        for sym in self.symbols:
            d = data[sym]
            for i in range(0, len(d.index)):
                self.strategy.handle(sym, i, data)

        self.strategy.orders.sort(key=lambda o: o.timestamp)

    def analyse(self):
        pass

    def report(self):
        pass

    def get_orders(self):
        return self.strategy.orders
    
    def get_benchmark(self, sym, start_date, end_date):
        b_values = Market.get_stock(sym,
                                    start_date,
                                    end_date)
        benchmark = b_values['close']
        return benchmark

    
class EventProfiler(BaseAnalyst):
    def __init__(self, symbols, strategy, start_date, end_date,
                 forward=20, backward=20):
        self.symbols = symbols
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.forward = forward
        self.backward = backward

    def analyse(self, benchmark=None):
        orders = self.strategy.orders
        windows = []
        for order in orders:
            timestamp = order.timestamp
            sym = order.symbol
            df = Market.get_stock(sym)
            index = df.index.searchsorted(timestamp)
            
            if index < self.backward or (len(df.index)-index-1) < self.forward:
                continue

            window = df.ix[index-self.backward:index+self.forward+1]
            close = window['close']
            norm_close = close / close.ix[self.backward] - 1
            windows.append(norm_close.values)
        if not windows:
            print('no event')
            return
        m = np.mean(windows, 0)
        plt.plot(range(-self.backward, self.forward+1), m)
        plt.axhline(0, color='black')
        plt.axvline(0, color='black')        
        plt.show()

        #return histgram for n-day after
        nforward = 2
        returns = []
        for window in windows:
            returns.append(window[self.forward+nforward])
            
        plt.hist(returns, 50)
        plt.show()
        
class BackTester(BaseAnalyst):
    def __init__(self, init_cash, symbols, strategy, start_date, end_date):
        """
        """
        super(BackTester, self).__init__(symbols, strategy, start_date, end_date)
        self.portfolio = Portfolio(init_cash)

    def analyse(self, benchmark_sym=None):
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

        benchmark = None
        if benchmark_sym:
            benchmark = self.get_benchmark(benchmark_sym,
                                           self.start_date,
                                           self.end_date)

        self.report(trade_days, pd.Series(values), benchmark)

    def report(self, timestamps, values, benchmark=None):
        k = 252
        returns = ind.returnize(values)
        cum_return = (returns+1).cumprod()
        avg_return = returns.mean()
        std_return = returns.std()
        sharpe_ratio = ind.sharpe_ratio(returns, k)

        if benchmark is not None:
            use_benchmark = True
        else:
            use_benchmark = False
            
        if use_benchmark:
            b_returns = ind.returnize(benchmark)
            b_cum_return = (b_returns+1).cumprod()
            b_avg_return = b_returns.mean()
            b_std_return = b_returns.std()
            b_sharpe_ratio = ind.sharpe_ratio(b_returns, k)

        # print("The final value of the portfolio is {}".format(values[-1])) 
        print("detail of the performance of the portfolio")
        print("{} to {}".format(timestamps[0], timestamps[-1]))

        print("Sharpe Ratio of Fund: {}".format(sharpe_ratio))
        if use_benchmark:
            print("Sharpe Ratio of benchmark: {}".format(b_sharpe_ratio))

        # print("Total Return of Fund: {}".format(cum_return[-1]))
        # if benchmark:
        #     print("Total Return of benchmark: {}".format(b_cum_return[-1]))
        print("Standard Deviation of Fund: {}".format(std_return))
        if use_benchmark:
            print("Standard Deviation of benchmark: {}".format(b_std_return))
            
        print("Average Daily Return of Fund: {}".format(avg_return))
        if use_benchmark:
            print("Average Daily Return of benchmar: {}".format(b_avg_return))

        plt.plot(timestamps, cum_return)
        if use_benchmark:
            plt.plot(timestamps, b_cum_return)
            plt.legend(['Sim', 'Benchmark'])
        plt.show()
        

def capm(symbol, index, start_date, end_date, visual=False):
    s = Market.get_stock(symbol, start_date, end_date)
    i = Market.get_stock(index, start_date, end_date)
    y = s['close']
    y = ind.returnize(y)
    x = i.ix[s.index]['close']
    x = ind.returnize(x)
    X = [[a] for a in x.values]

    regr = linear_model.LinearRegression(fit_intercept=True)

    regr.fit(X[1:], y[1:])
    beta = regr.coef_[0]
    alpha = regr.intercept_

    if visual:
        plt.scatter(x.values, y.values)
        plt.plot(X, regr.predict(X), 'r')
        plt.show()
    return beta, alpha
            
if __name__ == '__main__':
    start_date = datetime.datetime(2014, 5, 1)
    end_date = datetime.datetime(2014, 11, 13)
    
    # symbols = Market.get_symbol_list()
    # symbols = [s for s in symbols if s[2] == '6'][0:10]

    # strategy = TestStrategy()

    # # tester = BackTester(10000, symbols, strategy, start_date, end_date)
    # tester = EventProfiler(symbols, strategy, start_date, end_date)
    # tester.run()
    # orders = tester.get_orders()
    # tester.analyse()
    symbols = Market.get_symbol_list('SH')
    index = 'SH999999'
    if index in symbols:
        symbols.remove(index)

    symbols = ['SH600881', 'SH600064', 'SH600739', 'SH600219', 'SH600362', 'SH600028', 'SH601088', 'SH601989', 'SH600750', 'SH600298', 'SH601607']
    results = []
    i = 0
    size = len(symbols)
    for symbol in symbols:
        i += 1
        print('{}:{}/{}'.format(symbol, i, size))
        beta, alpha = capm(symbol, 'SH999999', start_date, end_date)
        print(beta, alpha)
        results.append((symbol, beta, alpha))

    # results.sort(key=lambda s: s[2], reverse=True)
    # print(results[0:20])
