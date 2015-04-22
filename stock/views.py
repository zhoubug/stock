from stock import app
from model import Market
import data
from analyse import capm
from flask import render_template, request, flash, redirect, url_for
from forms import AnalyseForm
from strategy import strategies
import algorithms as algos
from algorithms import test
import json
from docutils.core import publish_parts
from zipline import TradingAlgorithm

from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)

tasks_dict = {}


@app.route('/')
def home():
    return redirect(url_for('stocks'))


@app.route('/stocks')
def stocks():
    symbols = data.get_basics()
    return render_template('home.html', symbols=symbols)


@app.route('/stock/<code>')
def stock(code):
    stock = data.get_basics(code)
    regr = capm(code, 'sh', '2015-01-01', '2015-04-21')

    return render_template('stock.html', code=code,
                           stock=stock, capm=regr)

@app.route('/_stock/<sym>')
def _stock(sym):
    stock = Market.get_stock(sym)
    return stock.prices.to_json(orient="split")

@app.route('/_scatter/<sym>')
def _scatter(sym):
    start_date = request.args.get('start', None)
    end_date = request.args.get('end', None)

    base = "SH999999"
    x, y, beta, alpha = capm(sym, base)
    data = {}
    data['points'] = zip(x, y)
    data['beta'] = beta
    data['alpha'] = alpha
    return json.dumps(data)

@app.route('/analyse', methods=["GET", "POST"])
def analyse():
    form = AnalyseForm(request.form)
    if request.method == "POST":
        prefix = form.symbols.data
        symbols = filter(lambda s: s.startswith(prefix), data.get_basics().index)

        start = form.start.data
        end = form.end.data
        strategy = form.strategy.data
        analysts = form.analysts.data
        parameters = form.parameters.data
        kwargs = [ps.split('=') for ps in parameters.split(';')]
        kwargs = {v[0]: v[1] for v in kwargs if len(v) == 2}

        d = data.get_hist('600000')
        algo = TradingAlgorithm(initialize=test.initialize,
                                handle_data=test.handle_data)
        q.enqueue(algo.run, d)
    return render_template("analyse.html", form=form,
                           strategies=strategies.values(),
                           publish_parts=publish_parts)

@app.route('/compare')
def compare():
    syms = request.args.get('symbols').split(';')
    series = {}
    for sym in syms:
        stock = Market.get_stock(sym)
        close = stock.prices.close
        series[sym] = close.to_json(orient="split")
    return render_template('compare.html', data=series)


@app.route('/task/<id>')
def task(id):
    task = tasks_dict[id]
    if task.ready():
        result = task.result

        p_portfolio, p_benchmark = result[BackTester.name]
        window_buy, window_sell = result[EventProfiler.name]

        series = {}
        properties = {}
        windows = {}
        series["result"] = p_portfolio.values.to_json(orient="split")
        series["benchmark"] = p_benchmark.values.to_json(orient="split")
        properties["result"] = p_portfolio
        properties["benchmark"] = p_benchmark
        if window_buy is not None:
            windows["buy"] = window_buy.tolist()
        if window_sell is not None:
            windows["sell"] = window_sell.tolist()
        return render_template("result.html",
                               returns=series, properties=properties,
                               windows=windows)
    else:
        return 'task not ready'
