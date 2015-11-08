from zipline.api import order_target, record, symbol, history, add_history, order

import logbook
log = logbook.Logger('test')

def initialize(context):
    # Register 2 histories that track daily prices,
    # one with a 100 window and one with a 300 day window
    context.N = 5 + 1
    context.k = 0.7
    add_history(context.N, '1d', 'close')
    add_history(context.N, '1d', 'open')
    add_history(context.N, '1d', 'high')
    add_history(context.N, '1d', 'low')

    context.i = 0
    context.invested = False

def handle_data(context, data):
    # Skip first 300 days to get full windows
    context.i += 1
    if context.i < context.N:
        return

    # Compute averages
    # history() has to be called with the same params
    # from above and returns a pandas dataframe.
    c = history(context.N, '1d', 'close')
    o = history(context.N, '1d', 'open')
    h = history(context.N, '1d', 'high')
    l = history(context.N, '1d', 'low')
    for sym in data:
        # Trading logic
        hh = h[sym].ix[:-1].max()
        hc = c[sym].ix[:-1].max()
        lc = c[sym].ix[:-1].min()
        ll = l[sym].ix[:-1].min()
        r = max(hh-lc, hc-ll)
        upper = data[sym].open + context.k * r
        lower = data[sym].open - context.k * r

        if short_mavg[sym] > long_mavg[sym] and not context.invested:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            order(sym, 10000, limit_price=data[sym].price)
            context.invested = True
        elif short_mavg[sym] < long_mavg[sym] and context.invested:
            order(sym, -10000, limit_price=data[sym].price)
            context.invested = False
        # Save values for later inspection
        # record(close=data[sym].price,
        #        short_mavg=short_mavg[sym],
        #        long_mavg=long_mavg[sym])
