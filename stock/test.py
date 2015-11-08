import zipline
import data
from algorithms import test
import pandas as pd
import matplotlib.pyplot as plt
from analyse import Simulator, BackTester
from strategy import TestStrategy
from model import Market

code = '600000'
start = '2014-01-01'
end = '2014-12-31'
# d = data.get_hist(code, start, end)
d = Market.get_stocks([code])

strategy = TestStrategy()
analyst = BackTester()
sim = Simulator(strategy)
sim.add_analyst('backtest', analyst)
sim.run(d, start, end)


# syms = ["002038.sz"]
# d = zipline.data.load_bars_from_yahoo(stocks=syms, start='2014-01-01', end='2014-12-31',)

# algo = zipline.TradingAlgorithm(initialize=test.initialize,
#                                 handle_data=test.handle_data,
#                                 namespace={},
#                                 capital_base=10e6)
# results = algo.run(d)

# fig = plt.figure()
# ax1 = fig.add_subplot(211)
# results.portfolio_value.plot(ax=ax1)

# ax2 = fig.add_subplot(212)
# results[['close', 'short_mavg', 'long_mavg']].plot(ax=ax2)

# buy = results.buy.fillna(False)
# sell = results.sell.fillna(False)
# ax2.plot(results[buy].index, results.short_mavg[buy],
#          '^', markersize=10, color='m')
# ax2.plot(results[sell].index, results.short_mavg[sell],
#          'v', markersize=10, color='k')
# plt.legend(loc=0)
# plt.show()
