# -*- coding: utf-8 -*-
from model import Market
from analyse import BackTester, BaseStrategy, EventProfiler
import datetime
from flask import Flask, render_template

name = "StockTA"
app = Flask(name)

@app.route('/')
def home():
    symbols = Market.get_symbol_list()
    return render_template('home.html', symbols=symbols)

@app.route('/stock/<sym>')
def stock(sym):
    prices = Market.get_stock(sym)
    return render_template('stock.html', sym=sym, prices=prices)

@app.route('/stocks')
def stocks():
    return 'stocks'

if __name__ == '__main__':
    app.run(port=8000, debug=True)
    
class TestStrategy(BaseStrategy):
    def handle(self, symbol, index, data):
        df = data[symbol]
        timestamps = df.index

        if index < 2:
            return
        day_0 = df.ix[timestamps[index]]
        day_1 = df.ix[timestamps[index-1]]
        day_2 = df.ix[timestamps[index-2]]
        
        
        #孤岛
        day_1_high = day_1.close if day_1.close > day_1.open else day_1.open
        
        if day_2.open > day_2.close and day_2.close > day_1_high and \
           day_0.open < day_0.close and day_0.open > day_1_high:
            self.add_order(symbol, timestamps[index], 200, day_0.close)            
        # if close_today / close_yest > 1.03:
        #     self.add_order(symbol, timestamps[index], 200, close_today)
            # if index+5 < len(timestamps):
            #     sell_timestamp = timestamps[index+5]
            # else:
            #     sell_timestamp = timestamps[-1]
            # self.add_order(symbol, sell_timestamp, 200,
            #                df.ix[sell_timestamp].close)

# symbols = ['SH600881', 'SH600064', 'SH600739', 'SH600219', 'SH600362', 'SH600028', 'SH601088', 'SH601989', 'SH600750', 'SH600298', 'SH601607']            
# strategy = TestStrategy()
# start_date = datetime.datetime(2014, 1, 1)
# end_date = datetime.datetime(2014, 11, 1)

# # tester = BackTester(1000000, symbols, strategy, start_date, end_date)
# tester = EventProfiler(symbols, strategy, start_date, end_date)
# tester.run()
# tester.analyse()
# orders = tester.get_orders()
# for o in orders:
#     print(o)
