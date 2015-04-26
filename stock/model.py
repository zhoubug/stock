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
    def get_stock(symbol, start_date=None, end_date=None):
        df = Market._get_stock(symbol)
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
    def _get_stock(symbol):
        if symbol not in Market._cache:
            hist = data.get_hist(symbol)
            full = hist.reindex(trading_days)
            full['volume'].fillna(0, inplace=True)
            full['turnover'].fillna(0, inplace=True)
            full['p_change'].fillna(0, inplace=True)
            full['close'].fillna(method='pad', inplace=True)
            full['price'].fillna(method='pad', inplace=True)
            Market._cache[symbol] = full
        return Market._cache[symbol]


class Trader():
    # fee parameters which will be a list
    # in the list, value in (0, 1) will be multipled by order value
    # value more than 1 will be added
    # for example, if sell fee is [0.0008, 2]
    # then fee = 0.0008*order_price + 2
    fees = {'buy': [0.0008], 'sell': [0.0008, 1]}

    @staticmethod
    def make_order(portfolio, order):
        price = order.share*order.price
        if price > 0:     # buy
            fee = Trader.fees['buy']
        else:
            fee = Trader.fees['sell']
        total_fee = 0
        for f in fee:
            if f >= 1:          # fee by order
                total_fee += 1
            else:               # percentage by price
                total_fee += abs(price) * f
        total_price = price + total_fee

        if total_price > portfolio.cash:
            # no money to buy new stock
            pass
        else:
            portfolio.cash -= total_price
            portfolio.positions[order.symbol] += order.share
        return total_fee


class Portfolio():
    """
    is current cash and stocks
    """
    def __init__(self, init_cash):
        self.cash = init_cash
        self.positions = defaultdict(long)

    def get_value(self, date):
        value = self.cash
        for sym, share in self.positions.items():
            p = Market.get_stock_price(sym, date)
            value += p.close*share
        return value


class Order():
    def __init__(self, symbol, timestamp, share, price):
        self.symbol = symbol
        self.timestamp = timestamp
        self.share = share
        self.price = price

    def __str__(self):
        return '{}: {} {} {}'.format(self.timestamp, self.symbol,
                                     self.share, self.price)


class Property():
    k = 252

    def __init__(self, series):
        self.values = series
        returns = ind.returnize(series)
        self.cum_return = (returns+1).cumprod()
        self.avg_return = returns.mean()
        self.std_return = returns.std()
        self.sharpe_ratio = ind.sharpe_ratio(returns, Property.k)
