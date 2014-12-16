import pandas as pd
import pandas.io.data
import numpy as np
import matplotlib.pyplot as plt

import pytz
from datetime import datetime

import zipline as zp

from zipline.finance.slippage import FixedSlippage


stock = "002038.sz"


class MyAlgo(zp.TradingAlgorithm):
    def initialize(self):
        short_window = 10
        long_window = 50
        self.add_transform(zp.transforms.MovingAverage, 'short_ma', ['close'],
                           window_length=short_window)
        self.add_transform(zp.transforms.MovingAverage, 'long_ma', ['close'],
                           window_length=long_window)

        self.add_transform(zp.transforms.MovingAverage, 'short_vol', ['volumn'],
                           window_length=short_window)
        self.add_transform(zp.transforms.MovingAverage, 'long_vol', ['volumn'],
                           window_length=long_window)

        self.add_history()
        self.invested = False

    def handle_data(self, data):
        short_ma = data[stock].short_ma['close']
        long_ma = data[stock].long_ma['close']
        buy = False
        sell = False

        if short_ma > long_ma and not self.invested:
            self.order(stock, 100)
            self.invested = True
            buy = True

        elif short_ma < long_ma and self.invested:
            self.order(stock, -100)
            self.invested = False
            sell = True
        self.record(short_ma=short_ma, long_ma=long_ma, buy=buy, sell=sell)


def main():
    start = datetime(2006, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2014, 8, 25, 0, 0, 0, 0, pytz.utc)

    data = zp.utils.factory.load_bars_from_yahoo(stocks=[stock],
                                                 start=start,
                                                 end=end,
                                                 adjusted=True)
    algo = MyAlgo()
    perf = algo.run(data)

    fig = plt.figure()
    ax1 = fig.add_subplot(211,  ylabel='Price in $')
    data[stock]['close'].plot(ax=ax1, color='r', lw=2.)
    perf[['short_ma', 'long_ma']].plot(ax=ax1, lw=2.)

    ax1.plot(perf.ix[perf.buy].index, perf.short_ma[perf.buy],
             '^', markersize=10, color='m')
    ax1.plot(perf.ix[perf.sell].index, perf.short_ma[perf.sell],
             'v', markersize=10, color='k')

    ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
    perf.portfolio_value.plot(ax=ax2, lw=2.)

    ax2.plot(perf.ix[perf.buy].index, perf.portfolio_value[perf.buy],
             '^', markersize=10, color='m')
    ax2.plot(perf.ix[perf.sell].index, perf.portfolio_value[perf.sell],
             'v', markersize=10, color='k')

    plt.legend(loc=0)
    plt.gcf().set_size_inches(14, 10)
    plt.show()

if __name__ == '__main__':
    main()
