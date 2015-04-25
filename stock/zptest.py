import zipline
import data
from algorithms import test
import pandas as pd
import matplotlib.pyplot as plt
from analyse import Simulator, BackTester
from strategy import TestStrategy
from model import Market

# from zipline.utils import tradingcalendar_lse
import calendar_cn
from zipline.finance import trading
from zipline.algorithm import TradingAlgorithm
from zipline.finance.trading import TradingEnvironment

bm = '000001.SS'
trading.environment = TradingEnvironment(bm_symbol=bm, exchange_tz='Asia/Shanghai')
#trading.environment.trading_days = mid.index.normalize().unique()
# benchmark.index = benchmark.index.to_datetime().tz_localize('UTC')

trading.environment.trading_days = calendar_cn.trading_days

trading.environment.open_and_closes = pd.DataFrame(index=trading.environment.trading_days, columns=["market_open","market_close"])
trading.environment.open_and_closes.market_open = (trading.environment.open_and_closes.index + pd.to_timedelta(60*7,unit="T")).to_pydatetime()
trading.environment.open_and_closes.market_close = (trading.environment.open_and_closes.index + pd.to_timedelta(60*15+30,unit="T")).to_pydatetime()


from zipline.utils.factory import create_simulation_parameters
sim_params = create_simulation_parameters(
    start = pd.to_datetime("2014-01-01 08:30:00").tz_localize("Asia/Shanghai").tz_convert("UTC"),  #Bug in code doesn't set tz if these are not specified (finance/trading.py:SimulationParameters.calculate_first_open[close])
    end = pd.to_datetime("2014-12-31 16:30:00").tz_localize("Asia/Shanghai").tz_convert("UTC"),
    data_frequency = "daily",
    emission_rate = "daily",
    sids = ["600000"])


code = '600000'
start = '2014-01-01'
end = '2014-12-31'

benchmark = data.get_hist('sh', start, end)

d = Market.get_stocks([code], start, end)
# d[code].prices.index = d[code].prices.index.to_datetime().tz_localize('UTC')
d[code].prices['price'] = d[code].prices['close']
d = {k: v.prices for k, v in d.iteritems()}
d = pd.Panel(d)

# d = zipline.data.load_bars_from_yahoo(stocks=['AAPL'], start=start, end=end)
algo = zipline.TradingAlgorithm(initialize=test.initialize,
                                handle_data=test.handle_data,
                                namespace={},
                                capital_base=10e6,
                                sim_params=sim_params)
# results = algo.run(d, benchmark_return_source=d[code]['close'].pct_change())
results = algo.run(d)

fig = plt.figure()
ax1 = fig.add_subplot(211)
results.portfolio_value.plot(ax=ax1)

ax2 = fig.add_subplot(212)
results[['close', 'short_mavg', 'long_mavg']].plot(ax=ax2)

buy = results.buy.fillna(False)
sell = results.sell.fillna(False)
ax2.plot(results[buy].index, results.short_mavg[buy],
         '^', markersize=10, color='m')
ax2.plot(results[sell].index, results.short_mavg[sell],
         'v', markersize=10, color='k')
plt.legend(loc=0)
plt.show()
