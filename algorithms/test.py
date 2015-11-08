from zipline.api import order_target, record, symbol, history, add_history, order

import logbook
log = logbook.Logger('test')

def initialize(context):
    # Register 2 histories that track daily prices,
    # one with a 100 window and one with a 300 day window
    add_history(5, '1d', 'price')
    add_history(10, '1d', 'price')

    context.i = 0
    context.invested = False

def handle_data(context, data):
    # Skip first 300 days to get full windows
    context.i += 1
    if context.i < 10:
        return

    # Compute averages
    # history() has to be called with the same params
    # from above and returns a pandas dataframe.
    short_mavg = history(5, '1d', 'price').mean()
    long_mavg = history(10, '1d', 'price').mean()

    for sym in data:
        # sym = data.keys()[0]
        # sym = data.keys()[0]

        # Trading logic
        if short_mavg[sym] > long_mavg[sym] and not context.invested:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            order_target(sym, 5000)
            context.invested = True
        elif short_mavg[sym] < long_mavg[sym] and context.invested:
            order_target(sym, 0)
            context.invested = False
        # Save values for later inspection
        # record(close=data[sym].price,
        #        short_mavg=short_mavg[sym],
        #        long_mavg=long_mavg[sym])
