import zipline
import data
import pandas as pd
import matplotlib.pyplot as plt
from model import Market
from analyse import event_profile
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
trading.environment.open_and_closes.market_open = (trading.environment.open_and_closes.index + pd.to_timedelta(60*9+30,unit="m")).to_pydatetime()
trading.environment.open_and_closes.market_close = (trading.environment.open_and_closes.index + pd.to_timedelta(60*15,unit="m")).to_pydatetime()


from zipline.utils.factory import create_simulation_parameters
sim_params = create_simulation_parameters(
    start = pd.to_datetime("2014-01-01 09:30:00").tz_localize("Asia/Shanghai").tz_convert("UTC"),  #Bug in code doesn't set tz if these are not specified (finance/trading.py:SimulationParameters.calculate_first_open[close])
    end = pd.to_datetime("2014-12-31 15:00:00").tz_localize("Asia/Shanghai").tz_convert("UTC"),
    data_frequency = "daily",
    emission_rate = "daily",
    sids = ["600000"])

prefix = '000666'
codes = filter(lambda s: s.startswith(prefix), data.get_basics().index)
start = '2014-01-01'
end = '2015-04-30'

benchmark = data.get_hist('sh')

d = Market.get_stocks(codes, start, end)
# d[code].prices.index = d[code].prices.index.to_datetime().tz_localize('UTC')
# d[code].prices['price'] = d[code].prices['close']
d = pd.Panel(d)

with open('/home/leo/Workspace/stock/algorithms/aberration.py', 'r') as f:
    algo_text = f.read()
# d = zipline.data.load_bars_from_yahoo(stocks=['AAPL'], start=start, end=end)
algo = zipline.TradingAlgorithm(script=algo_text,
                                namespace={},
                                capital_base=100000,
                                sim_params=sim_params)
# results = algo.run(d, benchmark_return_source=d[code]['close'].pct_change())
results = algo.run(d)

fig = plt.figure()
ax1 = fig.add_subplot(311)

b_returns = algo.perf_tracker.all_benchmark_returns
benchmark = (b_returns+1).cumprod() - 1
benchmark.index = benchmark.index.to_pydatetime()
benchmark.plot(ax=ax1, label='benchmark')

(results.portfolio_value / results.portfolio_value[0] - 1).plot(ax=ax1, label='portfolio')

ax2 = fig.add_subplot(312)
results[['close']].plot(ax=ax2)

buy = results.buy.fillna(False)
sell = results.sell.fillna(False)
ax2.plot(results[buy].index, results.close[buy],
         '^', markersize=10, color='m')
ax2.plot(results[sell].index, results.close[sell],
         'v', markersize=10, color='k')

buy_window, sell_window = event_profile(algo, size=30)
ax3 = fig.add_subplot(313)
ax3.plot(range(-15, 15), buy_window, label='buy')
ax3.plot(range(-15, 15), sell_window, label='sell')

plt.legend(loc=0)
plt.show()
