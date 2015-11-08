import talib
from zipline.api import record, history, add_history, set_commission, get_datetime
from zipline.api import order, order_target, order_target_percent
from zipline.finance import commission
import numpy as np
import data as d

import logbook
log = logbook.Logger('test')

def initialize(context):
    # Register 2 histories that track daily prices,
    # one with a 100 window and one with a 300 day window
    add_history(25, '1d', 'price')
    set_commission(commission.PerDollar(0.0003))

    context.i = 0
    context.pct = 0.1

def handle_data(context, data):
    # Skip first 300 days to get full windows

    date = get_datetime()
    context.i += 1
    if context.i < 10:
        return

    prices = history(25, '1d', 'price')

    for sym in data:
        upper, middle, lower = talib.BBANDS(
            np.array(prices[sym]),
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )

        potential_buy = []

        buy = False
        sell = False
        if data[sym].price > upper[-1] and context.portfolio.positions[sym].amount == 0:
            # log.info('buy')
            # log.info(get_datetime())
            # log.info(data[sym].price)
            # log.info(upper[-1])
            order_target_percent(sym, 1.0, limit_price=data[sym].price)
        elif data[sym].price < middle[-1] and context.portfolio.positions[sym].amount > 0:
            # log.info('sell')
            # log.info(get_datetime())
            # log.info(data[sym].price)
            # log.info(middle[-1])
            order_target(sym, 0, limit_price=data[sym].price)
        # Save values for later inspection
        # record(close=data[sym].price, buy=buy, sell=sell)
