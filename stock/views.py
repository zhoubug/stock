from stock import app, celery
from model import Market
from analyse import BackTester, EventProfiler, Simulator
import datetime
from flask import render_template, request, flash
from forms import AnalyseForm
from strategy import strategies


tasks_dict = {}
@celery.task()
def simulate(simulator):
    simulator.run()
    simulator.analyse()
    return simulator.report()

@app.route('/')
def home():
    symbols = Market.get_symbol_list()
    return render_template('home.html', symbols=symbols)


@app.route('/stocks')
def stocks():
    symbols = Market.get_symbol_list()
    return render_template('home.html', symbols=symbols)    


@app.route('/stock/<sym>')
def stock(sym):
    return render_template('stock.html', sym=sym)

@app.route('/_stock/<sym>')
def _stock(sym):
    prices = Market.get_stock(sym)
    return prices.to_json(orient="split")

@app.route('/analyse', methods=["GET", "POST"])
def analyse():
    form = AnalyseForm(request.form)
    if request.method == "POST":
        prefix = form.symbols.data
        symbols = filter(lambda s: s.startswith(prefix), Market.get_symbol_list())

        start = form.start.data
        end = form.end.data
        strategy = form.strategy.data
        parameters = form.parameters.data
        kwargs = [ps.split('=') for ps in parameters.split(';')]
        kwargs = {v[0]: v[1] for v in kwargs if len(v) == 2}
        simulator = Simulator(symbols, strategies[strategy](**kwargs), start, end)
        
        tester = BackTester(100000)
        profile = EventProfiler()
        simulator.add_analyst('backtest', tester)
        simulator.add_analyst('profile', profile)

        r = simulate.delay(simulator)
        tasks_dict[r.id] = r
        flash('task added')
        # simulator.run()
        # simulator.analyse()
        # p_portfolio, p_benchmark = tester.report()

        # window_buy, window_sell = profile.report()
        # series = {}
        # properties = {}
        # windows = {}
        # series["result"] = p_portfolio.values.to_json(orient="split")
        # series["benchmark"] = p_benchmark.values.to_json(orient="split")
        # properties["result"] = p_portfolio
        # properties["benchmark"] = p_benchmark
        # if window_buy is not None:
        #     windows["buy"] = window_buy.tolist()
        # if window_sell is not None:
        #     windows["sell"] = window_sell.tolist()
        # return render_template("analyse.html", form=form,
        #                        orders=simulator.get_orders(),
        #                        returns=series, properties=properties,
        #                        windows=windows, result=tester.result)
    
    return render_template("analyse.html", form=form)
    
@app.route('/compare')
def compare():
    syms = request.args.get('symbols').split(';')
    series = {}
    for sym in syms:
        price = Market.get_stock(sym)
        close = price.close
        series[sym] = close.to_json(orient="split")
    return render_template('compare.html', data=series)

@app.route('/tasks')
def tasks():
    return render_template('tasks.html', tasks=tasks_dict.values())


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
    
