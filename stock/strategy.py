# -*- coding: utf-8 -*-
from analyse import BaseStrategy
import inspect
import sys


class TestStrategy(BaseStrategy):
    """
    parameters:
    `return`:
    """
    name = "Test Strategy"
    
    def handle(self, symbol, index, data):
        stock = data[symbol]
        timestamps = stock.timestamps()

        if index < 2:
            return
        # day_0 = df.ix[timestamps[index]]
        # day_1 = df.ix[timestamps[index-1]]
        # day_2 = df.ix[timestamps[index-2]]
        
        # #孤岛
        # day_1_high = day_1.close if day_1.close > day_1.open else day_1.open
        
        # if day_2.open > day_2.close and day_2.close > day_1_high and \
        #    day_0.open < day_0.close and day_0.open > day_1_high:
        #     self.add_order(symbol, timestamps[index], 200, day_0.close)

        close_today = stock.get_price_index(index).close
        close_yest = stock.get_price_index(index-1).close

        ratio = float(self.parameters.get("return", 0.03))
        if (close_today - close_yest)/close_yest > ratio:
            self.add_order(symbol, timestamps[index], 1000, close_today)
            if index+5 < len(timestamps):
                sell_timestamp = timestamps[index+5]
            else:
                sell_timestamp = timestamps[-1]
            self.add_order(symbol, sell_timestamp, -1000,
                           stock.get_price_timestamp(sell_timestamp).close)


class DualThrust(BaseStrategy):
    """
    
    """
    name = "Dual Thrust"
    
    def handle(self, symbol, index, data):
        stock = data[symbol]
        timestamps = stock.timestamps()

        if index < 4:
            return
        n = 4
        k = 0.7
        p_today = stock.get_price_index(index)
        window = stock.get_prices_index(index-n, index)
        hh = window.high.max()
        hc = window.close.max()
        lc = window.close.min()
        ll = window.low.min()
        r = max(hh-lc, hc-ll)
        threshold = p_today.open + k*r
        if p_today.low <= threshold and p_today.high >= threshold:
            self.add_order(symbol, timestamps[index], 1000, threshold)
            if index+4 < len(timestamps):
                sell_timestamp = timestamps[index+4]
            else:
                sell_timestamp = timestamps[-1]
            self.add_order(symbol, sell_timestamp, -1000,
                           stock.get_price_timestamp(sell_timestamp).open)
            
        
strategies = {t[0]: t[1] for t in inspect.getmembers(sys.modules[__name__],
                                                     lambda x: inspect.isclass(x) and issubclass(x, BaseStrategy) and x != BaseStrategy)}
