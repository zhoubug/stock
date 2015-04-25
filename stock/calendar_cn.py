import pandas as pd
import pytz

from datetime import datetime, timedelta
from dateutil import rrule
from functools import partial
import data

sh = data.get_hist('sh')
# start = sh.index[0]
# end_base = pd.Timestamp('today', tz='UTC')
# # Give an aggressive buffer for logic that needs to use the next trading
# # day or minute.
# end = end_base + timedelta(days=365)

def get_non_trading_days(start, end):
    sh = data.get_hist('sh')
    # reverse to get non trading_days
    day = pd.tseries.offsets.CDay(holidays=sh.index)
    return pd.date_range(start=start,
                         end=end,
                         freq=day)

non_trading_days = get_non_trading_days(sh.index[0], sh.index[-1])
trading_day = pd.tseries.offsets.CDay(holidays=non_trading_days)


def get_trading_days(start, end, trading_day=trading_day):
    return pd.date_range(start=start.date(),
                         end=end.date(),
                         freq=trading_day).tz_localize('UTC')

trading_days = get_trading_days(sh.index[0], sh.index[-1])


# def get_early_closes(start, end):
#     # 1:00 PM close rules based on
#     # http://quant.stackexchange.com/questions/4083/nyse-early-close-rules-july-4th-and-dec-25th # noqa
#     # and verified against http://www.nyse.com/pdfs/closings.pdf

#     # These rules are valid starting in 1993

#     start = canonicalize_datetime(start)
#     end = canonicalize_datetime(end)

#     start = max(start, datetime(1993, 1, 1, tzinfo=pytz.utc))
#     end = max(end, datetime(1993, 1, 1, tzinfo=pytz.utc))

#     # Not included here are early closes prior to 1993
#     # or unplanned early closes

#     early_close_rules = []

#     day_after_thanksgiving = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=11,
#         # 4th Friday isn't correct if month starts on Friday, so restrict to
#         # day range:
#         byweekday=(rrule.FR),
#         bymonthday=range(23, 30),
#         cache=True,
#         dtstart=start,
#         until=end
#     )
#     early_close_rules.append(day_after_thanksgiving)

#     christmas_eve = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=12,
#         bymonthday=24,
#         byweekday=(rrule.MO, rrule.TU, rrule.WE, rrule.TH),
#         cache=True,
#         dtstart=start,
#         until=end
#     )
#     early_close_rules.append(christmas_eve)

#     friday_after_christmas = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=12,
#         bymonthday=26,
#         byweekday=rrule.FR,
#         cache=True,
#         dtstart=start,
#         # valid 1993-2007
#         until=min(end, datetime(2007, 12, 31, tzinfo=pytz.utc))
#     )
#     early_close_rules.append(friday_after_christmas)

#     day_before_independence_day = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=7,
#         bymonthday=3,
#         byweekday=(rrule.MO, rrule.TU, rrule.TH),
#         cache=True,
#         dtstart=start,
#         until=end
#     )
#     early_close_rules.append(day_before_independence_day)

#     day_after_independence_day = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=7,
#         bymonthday=5,
#         byweekday=rrule.FR,
#         cache=True,
#         dtstart=start,
#         # starting in 2013: wednesday before independence day
#         until=min(end, datetime(2012, 12, 31, tzinfo=pytz.utc))
#     )
#     early_close_rules.append(day_after_independence_day)

#     wednesday_before_independence_day = rrule.rrule(
#         rrule.MONTHLY,
#         bymonth=7,
#         bymonthday=3,
#         byweekday=rrule.WE,
#         cache=True,
#         # starting in 2013
#         dtstart=max(start, datetime(2013, 1, 1, tzinfo=pytz.utc)),
#         until=max(end, datetime(2013, 1, 1, tzinfo=pytz.utc))
#     )
#     early_close_rules.append(wednesday_before_independence_day)

#     early_close_ruleset = rrule.rruleset()

#     for rule in early_close_rules:
#         early_close_ruleset.rrule(rule)
#     early_closes = early_close_ruleset.between(start, end, inc=True)

#     # Misc early closings from NYSE listing.
#     # http://www.nyse.com/pdfs/closings.pdf
#     #
#     # New Year's Eve
#     nye_1999 = datetime(1999, 12, 31, tzinfo=pytz.utc)
#     if start <= nye_1999 and nye_1999 <= end:
#         early_closes.append(nye_1999)

#     early_closes.sort()
#     return pd.DatetimeIndex(early_closes)

# early_closes = get_early_closes(start, end)


# def get_open_and_close(day, early_closes):
#     market_open = pd.Timestamp(
#         datetime(
#             year=day.year,
#             month=day.month,
#             day=day.day,
#             hour=9,
#             minute=31),
#         tz='US/Eastern').tz_convert('UTC')
#     # 1 PM if early close, 4 PM otherwise
#     close_hour = 13 if day in early_closes else 16
#     market_close = pd.Timestamp(
#         datetime(
#             year=day.year,
#             month=day.month,
#             day=day.day,
#             hour=close_hour),
#         tz='US/Eastern').tz_convert('UTC')

#     return market_open, market_close


# def get_open_and_closes(trading_days, early_closes):
#     open_and_closes = pd.DataFrame(index=trading_days,
#                                    columns=('market_open', 'market_close'))

#     get_o_and_c = partial(get_open_and_close, early_closes=early_closes)

#     open_and_closes['market_open'], open_and_closes['market_close'] = \
#         zip(*open_and_closes.index.map(get_o_and_c))

#     return open_and_closes

# open_and_closes = get_open_and_closes(trading_days, early_closes)
