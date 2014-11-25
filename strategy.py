# -*- coding: utf-8 -*-
from analyse import BaseStrategy
import inspect
import sys

class TestStrategy(BaseStrategy):
    """
    parameters:
    `return`:
    """
    def handle(self, symbol, index, data):
        df = data[symbol]
        timestamps = df.index

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
        close_today = df.ix[timestamps[index]].close
        close_yest = df.ix[timestamps[index-1]].close

        ratio = float(self.parameters.get("return", 0.3))
        if close_today / close_yest > ratio:
            self.add_order(symbol, timestamps[index], 200, close_today)
            if index+5 < len(timestamps):
                sell_timestamp = timestamps[index+5]
            else:
                sell_timestamp = timestamps[-1]
            self.add_order(symbol, sell_timestamp, -200,
                           df.ix[sell_timestamp].close)


            
strategies = {t[0]: t[1] for t in inspect.getmembers(sys.modules[__name__],
                                                     lambda x: inspect.isclass(x) and issubclass(x, BaseStrategy) and x != BaseStrategy)}
