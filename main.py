# -*- coding: utf-8 -*-
from model import Market
from analyse import BackTester, BaseStrategy, EventProfiler
import datetime
from flask import Flask, render_template, request, jsonify, json
from forms import AnalyseForm
from strategy import strategies
import pandas as pd

name = "StockTA"
app = Flask(name)
app.config.from_object("settings")

@app.route('/')
def home():
    symbols = Market.get_symbol_list()
    return render_template('home.html', symbols=symbols)

@app.route('/stock/<sym>')
def stock(sym):
    prices = Market.get_stock(sym)
    return render_template('stock.html', sym=sym, prices=prices)

@app.route('/_stock/<sym>')
def _stock(sym):
    prices = Market.get_stock(sym)
    return prices.to_json(orient="split")

@app.route('/analyse', methods=["GET", "POST"])
def analyse():
    form = AnalyseForm(request.form)
    series = None
    if request.method == "POST":
        symbols = form.symbols.data
        start = form.start.data
        end = form.end.data
        strategy = form.strategy.data

        tester = BackTester(100000, symbols, strategies[strategy](),
                            start, end)
        tester.run()
        trade_days, values, bench = tester.analyse(benchmark_sym="SH999999")
        
        series = {}
        series["result"] = values.to_json(orient="split")
        series["benchmark"] = bench.to_json(orient="split")
    return render_template("analyse.html", form=form, data=series)
    
@app.route('/compare')
def compare():
    syms = request.args.get('symbols').split(';')
    series = {}
    for sym in syms:
        price = Market.get_stock(sym)
        close = price.close
        series[sym] = close.to_json(orient="split")
    return render_template('compare.html', data=series)

@app.route('/stocks')
def stocks():
    return 'stocks'

if __name__ == '__main__':
    app.run(port=8000, debug=True)
    

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
