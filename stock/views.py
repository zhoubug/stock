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

from jobs import scheduler, run_analyse


redis_conn = Redis()
q = Queue(connection=redis_conn)

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
        print(symbols)
        start = form.start.data
        end = form.end.data

        parameters = form.parameters.data
        kwargs = [ps.split('=') for ps in parameters.split(';')]
        kwargs = {v[0]: v[1] for v in kwargs if len(v) == 2}

        job = q.enqueue(run_analyse,
                        test.initialize, test.handle_data,
                        symbols, start, end)
        # job_dict[job.id] = job

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

@app.route('/jobs')
def jobs():
    jobs = data.get_results()
    scheduled_jobs = scheduler.get_jobs(with_times=True)
    return render_template('jobs.html', jobs=jobs,
                           scheduled=scheduled_jobs)

import matplotlib.pyplot as plt, mpld3

@app.route('/job/<id>')
def job(id):
    result = data.get_result(id)
    if result:
        parameters = result['parameters']
        orders = sorted(result['orders'].values(), key=lambda o: o.dt)
        results = result['results']
        report = result['report']

        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        results.portfolio_value.plot(ax=ax1)

        ax2 = fig.add_subplot(212)
        results[['close', 'short_mavg', 'long_mavg']].plot(ax=ax2)

        buy = results.buy.fillna(False)
        sell = results.sell.fillna(False)
        ax2.plot(results[buy].index, results.short_mavg[buy],
                 '^', markersize=10, color='m')
        ax2.plot(results[sell].index, results.short_mavg[sell],
                 'v', markersize=10, color='k')
        plt.legend(loc=0)

        fig = mpld3.fig_to_html(fig)
        return render_template('result.html',
                               fig=fig,
                               report=report,
                               orders=orders)
    else:
        return 'task not done'

@app.route('/job/cancel/<id>')
def cancel(id):
    scheduler.cancel(id)
    return redirect(url_for('jobs'))

@app.route('/result/delete/<id>')
def delete_result(id):
    data.delete_result(id)
    return redirect(url_for('jobs'))
