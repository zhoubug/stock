from collections import defaultdict
import data
import indicators as ind
from calendar_cn import trading_days


def trade_index(df, start_date, end_date):
        if start_date:
            start_i = df.index.searchsorted(start_date)
        else:
            start_i = 0

        if end_date:
            end_i = df.index.searchsorted(end_date)
            if end_i < len(df.index) and df.index[end_i] == end_date:
                end_i += 1
        else:
            end_i = len(df.index)
        return start_i, end_i


class Market:
    _cache = {}
    _symbols = []

    @staticmethod
    def get_stocks(symbols, start_date=None, end_date=None):
        stocks = {}
        for symbol in symbols:
            stocks[symbol] = Market.get_stock(symbol, start_date, end_date)
        return stocks

    @staticmethod
    def get_stock(symbol, start_date=None, end_date=None, reindex=True):
        df = Market._get_stock(symbol, reindex)
        start_i, end_i = trade_index(df, start_date, end_date)
        return df.ix[start_i:end_i].copy()

    @staticmethod
    def get_stock_price(symbol, date):
        stock = Market._get_stock(symbol)
        return stock.get_price(date)

    @staticmethod
    def get_trade_days(start_date, end_date):
        sh = data.get_hist('sh')
        start_i, end_i = trade_index(sh, start_date, end_date)
        return sh.index[start_i: end_i]


    @staticmethod
    def get_symbol_list(market=None):
        if not Market._symbols:
            Market._symbols = data.get_basics().index
            Market._symbols.sort()
        if market:
            return filter(lambda s: s.startswith(market), Market._symbols)
        else:
            return Market._symbols

    @staticmethod
    def _get_stock(symbol, reindex=True):
        hist = data.get_h(symbol)
        if reindex:
            hist = hist.reindex(trading_days)
            hist['volume'].fillna(0, inplace=True)
            # hist['turnover'].fillna(0, inplace=True)
            # hist['p_change'].fillna(0, inplace=True)
            hist['close'].fillna(method='pad', inplace=True)
            hist['price'].fillna(method='pad', inplace=True)
        return hist
