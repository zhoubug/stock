from django.conf import settings
import tushare as ts
import pandas as pd
import os
import datetime

base_dir = os.path.join(settings.STATIC_ROOT, 'data')
INDEX = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb']

def update_basics():
    basics = ts.get_stock_basics()
    f = os.path.join(base_dir, 'basics.h5')
    basics.to_hdf(f, 'basics')

    today = datetime.date.today()
    current_year = today.year
    current_season = today.month / 3
    if current_season == 0:
        current_year -= 1
        current_season = 4
    length = 4 * 5

    year = current_year
    season = current_season
    for i in range(length):
        f = os.path.join(base_dir, 'basics-{0}-{1}.h5'.format(year, season))
        if os.path.exists(f):
            continue
        print(f)
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

def update_h():
    basics = get_basics()
    size = len(basics)
    count = 0

    f = os.path.join(base_dir, 'h.h5')
    for code in basics.index:
        print(code)
        try:
            h = ts.get_h_data(code)
            h.to_hdf(f, code)
            count += 1
        except Exception as e:
            print('error')
    return count, size


def update_hist():
    f = os.path.join(base_dir, 'hist.h5')
    for index in INDEX:
        print(index)
        try:
            hist = ts.get_hist_data(index)
            hist.to_hdf(f, index)
        except Exception as e:
            print(e)

    basics = get_basics()
    for code in basics.index:
        print(code)
        try:
            hist = ts.get_hist_data(code)
            hist.to_hdf(f, code)
        except Exception as e:
            print(e)


def get_h(code):
    f = os.path.join(base_dir, 'h.h5')
    df = pd.read_hdf(f, code)
    return df

def get_basics():
    f = os.path.join(base_dir, 'basics.h5')
    df = pd.read_hdf(f, 'basics')
    return df
