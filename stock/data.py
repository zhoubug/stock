import tushare as ts
import pandas as pd
import os
import datetime
import cPickle

BASE_DIR = (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'static', 'data')
INDEX = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb']
DATE_FORMAT = "%Y-%m-%d"

# operations for algorithm results
def save_result(id, result):
    filename = os.path.join(DATA_DIR, 'results', id)
    with open(filename, 'wb') as f:
        cPickle.dump(result, f)

def get_result(id):
    filename = os.path.join(DATA_DIR, 'results', id)
    with open(filename, 'rb') as f:
        result = cPickle.load(f)
    return result

def delete_result(id):
    f = os.path.join(DATA_DIR, 'results', id)
    os.remove(f)

def get_results():
    results_dir = os.path.join(DATA_DIR, 'results')
    ids = [f for f in os.listdir(results_dir)]
    results = {}
    for id in ids:
        result = get_result(id)
        results[id] = result
    return results


# for stock data
def _update_data(f, name, data):
    try:
        # if there is old data, append new to old
        pre = pd.read_hdf(f, name)
        p = pre.append(data)

        # clean duplicated data
        p = p.groupby(p.index).last()
        p.to_hdf(f, name)
    except Exception as e:
        data.to_hdf(f, name)

def time_range(start, end):
    if not end:
        d = datetime.date.today()
        end = d.strftime(DATE_FORMAT)
    if not start:
        d = datetime.datetime.strptime(end, DATE_FORMAT)
        delta = datetime.timedelta(days=365)
        start = (d - delta).strftime(DATE_FORMAT)
    return start, end

def last_report_season(date=None):
    if date:
        today = date
    else:
        today = datetime.date.today()
    current_year = today.year
    current_season = today.month / 3
    if current_season == 0:
        current_year -= 1
        current_season = 4
    return current_year, current_season

def update_basics():
    basics = ts.get_stock_basics()
    f = os.path.join(DATA_DIR, 'basics.h5')
    basics.to_hdf(f, 'basics')

    length = 4 * 5
    year, season = last_report_season()
    for i in range(length):
        f = os.path.join(DATA_DIR, 'basics-{0}-{1}.h5'.format(year, season))
        if os.path.exists(f):
            continue
        report = ts.get_report_data(year, season)
        report.to_hdf(f, 'report')

        profit = ts.get_profit_data(year, season)
        profit.to_hdf(f, 'profit')

        operation = ts.get_operation_data(year, season)
        operation.to_hdf(f, 'operation')

        growth = ts.get_growth_data(year, season)
        growth.to_hdf(f, 'growth')

        debtpaying = ts.get_debtpaying_data(year, season)
        debtpaying.to_hdf(f, 'debtpaying')

        cashflow = ts.get_cashflow_data(year, season)
        cashflow.to_hdf(f, 'cashflow')

        season -= 1
        if season == 0:
            season = 4
            year -= 1


def update_h(start=None, end=None):
    basics = get_basics()
    size = len(basics)
    count = 0

    start, end = time_range(start, end)

    f = os.path.join(DATA_DIR, 'h.h5')
    for code in basics.index:
        print(code)
        try:
            h = ts.get_h_data(code, start, end)
            _update_data(f, code, h)
            count += 1
        except Exception as e:
            print(e)
    return count, size


def update_hist(start=None, end=None):
    start, end = time_range(start, end)
    f = os.path.join(DATA_DIR, 'hist.h5')

    for index in INDEX:
        print(index)
        try:
            # for index, just rewrite all the data
            hist = ts.get_hist_data(index)
            # _update_data(f, index, hist)
            hist.to_hdf(f, index)
        except Exception as e:
            print(e)

    basics = get_basics()
    for code in basics.index:
        print(code)
        try:
            hist = ts.get_hist_data(code, start, end)
            _update_data(f, code, hist)
        except Exception as e:
            print(e)


def get_basics(code=None):
    f = os.path.join(DATA_DIR, 'basics.h5')
    df = pd.read_hdf(f, 'basics')
    if code:
        df = df.loc[code]
    return df


def _get_season_basics(year, season, name):
    if not year or not season:
        year, season = last_report_season()

    f = os.path.join(DATA_DIR, 'basics-{0}-{1}.h5'.format(year, season))
    df = pd.read_hdf(f, name)
    return df


def get_report(year=None, season=None):
    return _get_season_basics(year, season, 'report')

def get_profit(year=None, season=None):
    return _get_season_basics(year, season, 'profit')

def get_operation(year=None, season=None):
    return _get_season_basics(year, season, 'operation')

def get_growth(year=None, season=None):
    return _get_season_basics(year, season, 'growth')

def get_debtpaying(year=None, season=None):
    return _get_season_basics(year, season, 'debtpaying')

def get_cashflow(year=None, season=None):
    return _get_season_basics(year, season, 'cashflow')


def get_h(code):
    if code in INDEX:
        return get_hist(code)
    f = os.path.join(DATA_DIR, 'h.h5')
    df = pd.read_hdf(f, code)
    df['price'] = df['close']
    df.index = df.index.to_datetime().tz_localize('UTC')
    return df


def get_hist(code):
    f = os.path.join(DATA_DIR, 'hist.h5')
    df = pd.read_hdf(f, code)
    df['price'] = df['close']
    df.index = df.index.to_datetime().tz_localize('UTC')
    return df
