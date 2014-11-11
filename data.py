import pandas as pd
import os
import time

basedir = '/home/leo/tmp'


def read_history_file(filename):
    names = ['date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
    df = pd.read_csv(filename, delimiter=',', names=names,
                     skiprows=2, skip_footer=1, index_col='date',
                     parse_dates=True, )
    return df


def read_history_symble(symbol):
    filename = symbol + ".txt"
    fullpath = os.path.join(basedir, filename)
    return read_history_file(fullpath)


def read_symbol_list():
    filenames = os.listdir(basedir)
    symbols = [name.split('.')[0] for name in filenames]
    return symbols


def read_dir(basedir):
    history = {}
    filenames = os.listdir(basedir)
    for filename in filenames:
        print(filename)
        name = filename.split('.')[0]
        fullpath = os.path.join(basedir, filename)
        df = read_history_file(fullpath)
        history[name] = df
    return history

if __name__ == '__main__':
    sym = 'SH600000'
    l = read_symbol_list()
    print(l)
